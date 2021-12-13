import argparse
import datetime
import json
from datetime import date
import os
import pandas as pd
import geopandas
import pycountry
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from collections import Counter
import numpy as np
import plotly.express as px

def check_none(value):
    """Raises ValueError if value is type None, else returns value"""
    if isinstance(value, type(None)):
        raise ValueError
    return value

def find_country(country):
    """ .get retrieves data as class Country
    .search_fuzzy matching returns a list
    try a few ways to identify a match and
    return as soon as find something valid
    Input is country name (string)
    If no match found, return None"""
    try:
        hit = pycountry.countries.get(name=country)
        hit = check_none(hit)
        return hit
    except (LookupError, ValueError):
        try:
            hit = pycountry.countries.get(official_name=country)
            hit = check_none(hit)
            return hit
        except (LookupError, ValueError):
            try:
                hit = pycountry.countries.search_fuzzy(country)
                hit = check_none(hit)
                if type(hit) == list and len(hit) == 1:
                    return hit[0]
                raise ValueError
            except (LookupError, ValueError):
                try:
                    hit = pycountry.countries.search_fuzzy(country + ",")
                    hit = check_none(hit)
                    if isinstance(hit, list) and len(hit) == 1:
                        return hit[0]
                    else:
                        raise ValueError
                except (LookupError, ValueError):
                    return None

def assign_ISO(countries):
    """ Match country names with ISO codes
    Input: series of country names
    Returns: dictionary of matches
    :type countries: pd.Series """
    # Need to hard code a few countries that aren't registered using standard names, so
    # initializing the country_codes database with these irregular values
    country_codes = {"South Korea": "KOR", "Democratic Republic of Congo": "COD",
                     "Democratic Republic of the Congo": "COD", "UAE": "ARE"}

    # Identify the most likely 3-letter ISO code for each country
    failed_matches = list()
    for country in countries:
        if country not in country_codes.keys():
            # Need to query the pycountry package but it can fail for a
            # few reasons. Use function to avoid LookupError issues and
            # try all the different ways that might help to match a
            # country name to its ISO code
            hit = find_country(country)
            if not isinstance(hit, type(None)):
                country_codes[country] = hit.alpha_3
            else:
                failed_matches.append(country)
    # Print warning about failures and return successes as dictionary
    print("Could not assign country codes to: ", ", ".join(failed_matches))
    return country_codes

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

def main(args):
    # Set up country mapping
    countries_mapping = setup_geopandas()
    # Import data from github.com/owid/covid-19-data
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

    owid_stats["owid_total_vaccinations"] = str("{:,}".format(round(vaccine_nums[vaccine_nums["location"] ==
                                                          "World"].loc[vaccine_nums["date"] ==
                                                                       owid_stats["owid_most_recent_date"],
                                                                       "total_vaccinations"].item()/1000000))) + \
                                       " million"
    owid_stats["owid_daily_rate"] = str("{:,}".format(round(vaccine_nums[vaccine_nums["location"] ==
                                                "World"].loc[vaccine_nums["date"] ==
                                                             owid_stats["owid_most_recent_date"],
                                                             "daily_vaccinations_per_million"].item()))) + " per million"
    owid_stats["owid_total_countries"] = format(vaccine_locations["location"].nunique())

    # Identify number of vaccine manufacturers included in location totals (not the same as manufacturer-specific data)
    vaxTypes = set([item.strip() for countryList in vaccine_locations["vaccines"].to_list() for item in countryList.split(",")])
    owid_stats["owid_vaccine_types"] = format(len(vaxTypes))
    vaxPlatforms = pd.read_csv(args.platform_types, index_col="Manufacturer")

    missingInfo = [vax for vax in vaxTypes if vax not in vaxPlatforms.index]
    if len(missingInfo) > 0:
        exit("Missing platform information for " + ", ".join(missingInfo))

    # Plot worldwide distribution by vaccine type
    allVaxByCountry = dict(zip(vaccine_locations["iso_code"], vaccine_locations["vaccines"]))
    countryByVax = dict()
    for iso, vaccines in allVaxByCountry.items():
        for vax in vaccines.split(","):
            vax = vax.strip()
            countryCodes = countryByVax.get(vax, [])
            countryByVax[vax] = countryCodes + [iso]


    vaxPlatforms['countries']=vaxPlatforms.index.map(countryByVax)

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(20, 16))
    fig.patch.set_visible(False)
    ax1.axis('off')
    ax2.axis('off')

    for platform in set(list(vaxPlatforms["Type"])):
        vaccines = vaxPlatforms[vaxPlatforms["Type"] == platform]
        countries = [iso for country_list in vaccines["countries"]
                     for iso in country_list]
        counts = dict()
        for iso in countries:
            runningTot = counts.get(iso, 0)
            counts[iso] = runningTot + 1

        vaxPresence = pd.DataFrame.from_dict(counts, orient="index",
                                             columns=["count"])
        countries_mapping.boundary.plot(ax=ax1, edgecolor="black")

        countries_mapping = countries_mapping.merge(vaxPresence,
                                                    how="right",
                                                    right_index=True,
                                                    left_on="iso_a3")
        #countries_mapping['count'] =  countries_mapping['count'].fillna(0)


        countries_mapping.plot(column='count', ax=ax1, legend=True)
        ax1.set_title("Number of Single-Country Clinical Trials Recruiting by Country")

        #countries_mapping.boundary.plot(ax=ax2, edgecolor="black")
        #countries_mapping.plot(column='multi_countries_counts', ax=ax2,
        # legend=True, cmap="Purples")
        #ax2.set_title("Number of Multi-Country Clinical Trials Recruiting by Country")
        #ax2.annotate(f'Source: EBM Data Lab COVID-19 TrialsTracker, %s' %
        #             date.today().strftime("%b-%d-%Y"),
        #             xy=(0, 0), xycoords="axes points")

        plt.savefig(args.output_map + '.png', dpi=300, bbox_inches="tight")
        #plt.savefig(args.output_map + '.svg', bbox_inches="tight")

        exit(0)

    print(f'Wrote {args.output_map}.png and {args.output_map}.svg')

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
    parser.add_argument('output_map',
                        help='Path of the image files with the vaccine distribution map image',
                        type=str)
    args = parser.parse_args()
    main(args)
