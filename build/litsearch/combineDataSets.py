import pandas as pd
import os
import urllib.request
import requests
import datetime as dt

def update_AI(fname):
    # Download most up-to-date metadata from Allen AI COVID-19 dataset
    url = 'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/metadata.csv'
    urllib.request.urlretrieve(url, filename=fname)

def paper_info(row):
    """Queries metadata from bioRxiv or medRxiv based on paper DOI
    Accepts: Row formatted as review_sources df, must have "doi" and "publication"
    Returns: Row, updated as possible from *arxiv API """
    if row["publication"] in ["bioRxiv", "medRxiv"]:
        # Format URL for *rxiv API and convert metadata to dict from json response
        pub = row["publication"].lower()
        doi = row["doi"]
        url = "https://api.biorxiv.org/details/{0}/{1}".format(pub,doi)
        r = requests.get(url)
        paper_data = r.json()
        metadata = dict(paper_data["collection"][0])

        # Update the row with metadata retrieved
        row["URL"] = url
        for kwd in ["title", "authors", "date", "abstract"]:
            row[kwd] = metadata[kwd]
    return row

if __name__ == "__main__":
    # Update external data, if not updated yet today, and read
    metadata_fname = "./output/AllenAI-metadata.csv"
    print("Update Allen AI metadata")
    update_AI(metadata_fname)
    AIA_metadata = pd.read_csv(metadata_fname, low_memory=False)
    AIA_metadata = AIA_metadata.dropna(subset=["doi"])
    print("AIA has {0} sources".format(len(AIA_metadata)))

    # Update internal dataset, which is maintained with CI
    review_sources = pd.read_csv("./output/sources_cross_reference.tsv",
                                 sep="\t")
    review_sources = review_sources.dropna(subset=["doi"])
    review_sources.rename({"URL":"SecondaryURL"}, inplace=True, axis=1)
    print("COVID-19 review has examined {0} sources".format(len(review_sources)))

    # Add tracking from project to the Allen AI dataset
    combined = AIA_metadata.merge(review_sources,
                                  on="doi",
                                  how="outer")
    print("Combined set has {0} sources".format(len(combined)))

    # Remove duplicate columns
    to_rename = dict()
    for dup_col in ["title"]: # loop in case we end up with other duplicated info to remove
        combined[dup_col + "_x"].update(combined[dup_col + "_y"])
        combined.drop(dup_col + "_y", axis=1, inplace=True)
        to_rename[dup_col + "_x"] = dup_col
    combined.rename(to_rename, inplace=True, axis=1)

    # Retrieve data for internally referenced dois not in Allen AI dataset
    missing_dois = pd.Series(list(set(review_sources["doi"]).
                                  difference(set(AIA_metadata["doi"]))),
                             name="doi")
    missing = pd.merge(combined,
                       missing_dois.to_frame(),
                       on='doi',
                       how='inner',
                       left_index=True)
    missing.apply(paper_info, axis=1)
    for source in ["bioRxiv", "medRxiv"]:
        if len(missing[missing["publication"] == source]) > 0:
            print("Abstract retrieved from {0} for these DOIs:".format(source))
            print(list(missing[missing["publication"] == source]["doi"]))

    # Update combined with information from bioRxiv/medRxiv
    combined.set_index("doi", inplace=True)
    combined.update(missing.set_index("doi"))
    combined['doi'] = combined.index

    # Tabulate papers not in Allen AI and not available through bio/medRxiv API
    num_pubs_missing = missing['publication'].value_counts().to_dict()
    print("{0} unmatched references, {1} not in Allen AI, bioRxiv, medRxiv".format(
        sum(num_pubs_missing.values()),
        sum([num_pubs_missing[pub]
             for pub in num_pubs_missing.keys()
             if pub not in ["bioRxiv", "medRxiv"]])))

    combined.to_csv("./output/covid19-lit-all.tsv", sep="\t", index=False)
