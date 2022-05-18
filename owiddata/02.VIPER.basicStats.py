import argparse
from jsonFunctions import *
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup

def assign_platform_types(vaxtype):
    """The types of vaccines as categoried on trackvaccines.org differs
    somewhat from the categories we use here.
    See https://covid19.trackvaccines.org/types-of-vaccines/
    This function maps their categories (key) onto the section headings
    used in the manuscript (value)
    Input: string
    Output: string"""

    types = {"protein subunit": "subunit",
             "VLP": "subunit",
             "plasmid vectored": "DNA",
             "DNA": "DNA",
             "RNA": "RNA",
             "non replicating viral vector": "DNA",
             "replicating viral vector": "DNA",
             "inactivated": "whole virus",
             "live attenuated": "whole virus"
             }

    # If they add a new platform type (which seems unlikely), handle & throw error
    if vaxtype not in types.keys():
        # Update to raise issue
        print("Unknown vaccine platform:", vaxtype)
        exit(1)

    return types[vaxtype]

def retrieve_platform_types():
    """Use trackvaccines.org to scrape the website listing approved vaccines
    Returns: dataframe """
    vaccine_info = dict()
    vaccineHTML = urllib.request.urlopen('https://covid19.trackvaccines.org/vaccines/approved/')

    # Extract the HTML that makes the cards on the webpage (each card is a vax)
    soup = BeautifulSoup(vaccineHTML, "html5lib")
    body = soup.find('body')
    cards = body.find_all('li')

    # Iterate through the cards to extract information
    # Tags were identified empirically and are not self-evident
    for card in cards: # find all element of tag
        if card.find('a', {"class": "icon-link"}) is not None:
            vaccine_platform = card.find('a', {"class": "icon-link"}).get_text()
            if vaccine_platform.upper() != vaccine_platform: #DNA, RNA, VLP
                vaccine_platform = vaccine_platform.lower()
            vaccine_platform_type = assign_platform_types(vaccine_platform)
            vaccine_manf = card.find('span',
                                     {"class": "has-medium-font-size"}).get_text()
            vaccine_name = card.find('span',
                                     {"class": "has-large-font-size"}).get_text()
            link = card.find('a', href=True)
            vaccine_info[vaccine_name] = [vaccine_manf,
                                          vaccine_platform,
                                          vaccine_platform_type,
                                          link['href']]
    vaccine_df = pd.DataFrame.from_dict(vaccine_info, orient='index')
    vaccine_df.rename(mapper={0: "Company", 1: "Platform", 2: "Platform Type", 3: "URL"},
                      axis=1, inplace=True)
    vaccine_df.index.name = 'Vaccine'
    vaccine_df["Platform"] = vaccine_df["Platform"].replace("DNA","plasmid vectored")
    return vaccine_df

def create_table(vaccine_df, platformType):
    """For each vaccine platform, select a subset of the vaccine information table
    Input: dataframe, string
    Returns: string representing a table in markdown"""
    vaccines = vaccine_df[vaccine_df["Platform Type"] == platformType]
    numTypes = len(set(vaccines["Platform"].to_list()))
    if numTypes > 1:
        return vaccines[["Company", "Platform"]].to_markdown()
    else:
        return vaccines[["Company"]].to_markdown()

def main(args):
    # Read OWID stats collected thus far
    owid_stats = load_JSON(args.update_json)

    # Retrieve & store types of vaccines from https://covid19.trackvaccines.org
    vaxPlatforms = retrieve_platform_types()
    vaxPlatforms.to_csv(args.platform_types, index=True)

    # Count the number of vaccines being administered total & per technology type
    owid_stats["viper_vaccine_counts"] = format(len(vaxPlatforms))

    # Generate table of vaccines within each platform type
    for type in set(vaxPlatforms["Platform Type"]):
        owid_stats["viper_approved_" + "_".join(type.split())] = \
            create_table(vaxPlatforms, type)

    # Add to JSON file
    write_JSON(owid_stats, args.update_json)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('update_json',
                        help='Path of the JSON file with extracted statistics',
                        type=str)
    parser.add_argument('platform_types',
                        help='Path of the CSV file with the vaccine to platform mapping',
                        type=str)

    args = parser.parse_args()
    main(args)
