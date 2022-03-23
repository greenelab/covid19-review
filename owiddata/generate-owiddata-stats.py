import argparse
import datetime
import json
import os
import pandas as pd
import geopandas
import urllib.request
from bs4 import BeautifulSoup
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def platforms(vaxtype):
    """The types of vaccines as categoried on trackvaccines.org differs
    somewhat from the categories we use here.
    See https://covid19.trackvaccines.org/types-of-vaccines/
    This function maps their categories (key) onto the section headings
    used in the manuscript (value)
    Input: string
    Output: string"""

    types = {"Protein Subunit": "Subunit",
             "VLP": "Subunit",
             "Plasmid Vectored": "DNA",
             "DNA": "DNA",
             "RNA": "RNA",
             "Non Replicating Viral Vector": "DNA",
             "Replicating Viral Vector": "DNA",
             "Inactivated": "Whole Virus",
             "Live-Attenuated": "Whole Virus"
             }

    # If they add a new category (which seems unlikely), handle & throw error
    if vaxtype not in types.keys():
        print("Unknown vaccine platform:", vaxtype)
        return vaxtype

    return types[vaxtype]

def lowres_fix(world):
    """There is an issue with the map data source from geopandas where
    ISO codes are missing for several countries. This fix was proposed
    by @tommycarstensen at
    https://github.com/geopandas/geopandas/issues/1041

    :param world: dataframe (read in with geopandas)
    :return: dataframe (geopandas formatted)
    """
    world.loc[world['name'] == 'France', 'iso_a3'] = 'FRA'
    world.loc[world['name'] == 'Norway', 'iso_a3'] = 'NOR'
    world.loc[world['name'] == 'Somaliland', 'iso_a3'] = 'SOM'
    world.loc[world['name'] == 'Kosovo', 'iso_a3'] = 'RKS'
    return world

def setup_geopandas():
    countries_mapping = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    countries_mapping = lowres_fix(countries_mapping)
    countries_mapping = countries_mapping[(countries_mapping.name != "Antarctica") &
                                          (countries_mapping.iso_a3 != "-99")]
    return countries_mapping

def convert_date(git_date):
    '''Reformat git commit style datetimes (ISO 8601) to Month DD, YYYY.
    Throws a ValueError if git_date cannot be parsed as an ISO 8601 datetime.
    '''
    # 'Z' indicates Coordinated Universal Time (UTC)
    # Replace with '+00:00', which is the UTC representation recognized
    # by the parser
    # https://en.wikipedia.org/wiki/ISO_8601#Coordinated_Universal_Time_(UTC)
    git_date = git_date.replace('Z', '+00:00')

    # Remove the leading zero of the day
    # Assumes the year will not begin with 0
    return datetime.datetime.fromisoformat(git_date).strftime('%B %d, %Y').replace(' 0', ' ')

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
            vaccine_type = card.find('a', {"class": "icon-link"}).get_text()
            vaccine_category = platforms(vaccine_type)
            link = card.find('a', href=True)

            vaccine_manf = card.find('span',
                                     {"class": "has-medium-font-size"}).get_text()
            vaccine_name = card.find('span',
                                     {"class": "has-large-font-size"}).get_text()
            vaccine_info[vaccine_name] = [vaccine_manf,
                                          vaccine_type,
                                          vaccine_category,
                                          link['href']]
    vaccine_df = pd.DataFrame.from_dict(vaccine_info, orient='index')
    vaccine_df.rename(mapper={0: "Company", 1: "Type", 2: "Category", 3: "URL"},
                      axis=1, inplace=True)
    vaccine_df.index.name = 'Vaccine'
    vaccine_df["Type"] = vaccine_df["Type"].replace("DNA","Plasmid Vectored")
    return vaccine_df

def create_table(vaccine_df, category):
    """For each vaccine type, select a subset of the vaccine information table
    Input: dataframe, string
    Returns: string representing a table in markdown"""
    vaccines = vaccine_df[vaccine_df["Category"] == category]
    numTypes = len(set(vaccines["Type"].to_list()))
    if numTypes > 1:
        return vaccines[["Company", "Type"]].to_markdown()
    else:
        return vaccines[["Company"]].to_markdown()

def main(args):
    # Set up country mapping
    countries_mapping = setup_geopandas()

    # Create dictionary that will be exported as JSON
    owid_stats = dict()

    # Download data from a specific commit if the environment variable is set,
    # otherwise default to master
    commit = 'master'
    if('OWID_COMMIT_SHA' in os.environ):
        commit = os.environ['OWID_COMMIT_SHA']
        owid_stats['owid_commit_sha'] = os.environ['OWID_COMMIT_SHA']
    if('OWID_COMMIT_DATE' in os.environ):
        owid_stats['owid_commit_date'] = os.environ['OWID_COMMIT_DATE']
        owid_stats['owid_commit_date_pretty'] = convert_date(os.environ['OWID_COMMIT_DATE'])

    # Retrieve data from OWID
    locations_url = f'https://raw.githubusercontent.com/owid/covid-19-data/{commit}/public/data/vaccinations/locations.csv'
    vaccine_locations = pd.read_csv(locations_url, error_bad_lines=False)

    numbers_url = f'https://raw.githubusercontent.com/owid/covid-19-data/{commit}/public/data/vaccinations/vaccinations.csv'
    vaccine_nums = pd.read_csv(numbers_url, error_bad_lines=False)

    manufacturer_url = f'https://raw.githubusercontent.com/owid/covid-19-data/{commit}/public/data/vaccinations/vaccinations-by-manufacturer.csv'
    vaccine_manf = pd.read_csv(manufacturer_url , error_bad_lines=False)

    # Pull up-to-date statistics from data
    vaccine_locations['last_observation_date'] = pd.to_datetime(vaccine_locations['last_observation_date'])
    vaccine_nums['date'] = pd.to_datetime(vaccine_nums['date'])
    vaccine_manf['date'] = pd.to_datetime(vaccine_manf['date'])

    owid_stats["owid_most_recent_date"] = vaccine_nums['date'].max().strftime('%B %d, %Y').replace(' 0', ' ')

    owid_stats["owid_total_vaccinations"] = \
        str("{:,}".format(round(vaccine_nums[vaccine_nums["location"] == "World"].
                                loc[vaccine_nums["date"] ==
                                    owid_stats["owid_most_recent_date"],
                                    "total_vaccinations"].item()/1000000000))) + \
        " billion"
    owid_stats["owid_daily_rate"] = \
        str("{:,}".format(round(vaccine_nums[vaccine_nums["location"] == "World"].
                                loc[vaccine_nums["date"] ==
                                    owid_stats["owid_most_recent_date"],
                                    "daily_vaccinations_per_million"].item()))) + \
        " per million"
    owid_stats["owid_total_countries"] = \
        format(vaccine_locations["location"].nunique())

    # Identify number of vaccine manufacturers included in location totals (not the same as manufacturer-specific data)
    vaxTypes = set([item.strip() for countryList in
                    vaccine_locations["vaccines"].to_list()
                    for item in countryList.split(",")])
    owid_stats["owid_vaccine_types"] = format(len(vaxTypes))

    # Retrieve & store types of vaccines from https://covid19.trackvaccines.org
    vaxPlatforms = retrieve_platform_types()
    vaxPlatforms.to_csv(args.platform_types)

    # Count the number of vaccines being administered total & per technology type
    owid_stats["viper_vaccine_types"] = format(len(vaxPlatforms))
    numVax = vaxPlatforms["Type"].value_counts()

    # Generate table of vaccines within each type
    for category in set(vaxPlatforms["Category"]):
        owid_stats["viper_approved_" + category] = \
            create_table(vaxPlatforms, category)

    # Set the parameters color-coding the plots. Scale is the max candidates adminstered across all vaccine types.
    scale = max(numVax)
    cmap = mpl.cm.Purples
    norm = mpl.colors.BoundaryNorm(np.arange(0, scale + 1), cmap.N)

    # Transform list of vaccine candidate per iso code to list of ISO codes per vaccine candidate
    allVaxByCountry = dict(zip(vaccine_locations["iso_code"],
                               vaccine_locations["vaccines"]))
    countryByVax = dict()
    for iso, vaccines in allVaxByCountry.items():
        for vax in vaccines.split(","):
            vax = vax.strip()
            countryCodes = countryByVax.get(vax, [])
            countryByVax[vax] = countryCodes + [iso]

    # Add countries to vaccine platform info and plot each vaccine type
    vaxPlatforms['countries'] = vaxPlatforms.index.map(countryByVax)

    for platform in set(vaxPlatforms["Type"]):
        platformName = '_'.join(platform.split(' '))
        platformName = platformName.replace("-", "_")
        owid_stats["owid_" + platformName + "_count"] = \
            len(vaxPlatforms[vaxPlatforms["Type"] == platform])

        fig, ax = plt.subplots(1, 1, figsize=(6,4))
        ax.axis('off')

        vaccines = vaxPlatforms[vaxPlatforms["Type"] == platform].dropna()
        countries = [iso for country_list in vaccines["countries"]
                     for iso in country_list]
        counts = dict()
        for iso in countries:
            runningTot = counts.get(iso, 0)
            counts[iso] = runningTot + 1

        vaxPresence = pd.DataFrame.from_dict(counts, orient="index",
                                             columns=[platform])
        owid_stats["owid_" + platformName + "_countries"] = len(vaxPresence)
        countries_mapping.boundary.plot(ax=ax, edgecolor="black")

        mappingData = countries_mapping.merge(vaxPresence,
                                                    how="left",
                                                    right_index=True,
                                                    left_on="iso_a3")

        mappingData[platform] = mappingData[platform].fillna(0)
        mappingData.plot(column=platform, ax=ax,
                         legend=True, cmap=cmap, norm=norm,
                         legend_kwds={'shrink': 0.2})
        ax.set_title("Number of " + platform + " vaccines available worldwide")
        fig.tight_layout()

        plt.savefig(args.map_dir + "/" + platformName + '.png', dpi=300, bbox_inches="tight")
        plt.savefig(args.map_dir + "/" + platformName + '.svg', bbox_inches="tight")

        print(f'Wrote {args.map_dir + "/" + platformName + ".png"} and '
              f'{args.map_dir + "/" + platformName + ".svg"}')

        # The placeholder will be replaced by the actual SHA-1 hash in separate
        # script after the updated image is committed
        owid_stats['owid_' + platformName + "_map"] = \
            f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.map_dir}/{platformName}.png'

    with open(args.output_json, 'w') as out_file:
        json.dump(owid_stats, out_file, indent=2, sort_keys=True)
    print(f'Wrote {args.output_json}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('output_json',
                        help='Path of the JSON file with extracted statistics',
                        type=str)
    parser.add_argument('platform_types',
                        help='Path of the CSV file with the vaccine to platform mapping',
                        type=str)
    parser.add_argument('map_dir',
                        help='Path of directory containing image files with the vaccine distribution map images',
                        type=str)
    args = parser.parse_args()
    main(args)
