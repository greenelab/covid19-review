import pandas as pd
import os
import datetime
import argparse
import plydata as ply
import numpy as np
from jsonFunctions import write_JSON
from mapFunctions import setup_geopandas

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

def billions(count, decimals=0):
    """Cleans integer in the billions to make a string formatted as 'X billion', defaulting to integer"""
    try:
        int(count)
    except TypeError:
        return("Cannot convert count '{0}' to billions".format(count))
    return str(np.round(count/1000000000, decimals)) + " billion"

def main(args):
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

    # Retrieve all data from OWID that we need for the whole pipeline
    locations_url = f'https://raw.githubusercontent.com/owid/covid-19-data/{commit}/public/data/vaccinations/locations.csv'
    vaccine_locations = pd.read_csv(locations_url, error_bad_lines=False)

    numbers_url = f'https://raw.githubusercontent.com/owid/covid-19-data/{commit}/public/data/vaccinations/vaccinations.csv'
    vaccine_nums = pd.read_csv(numbers_url, error_bad_lines=False)

    manufacturer_url = f'https://raw.githubusercontent.com/owid/covid-19-data/{commit}/public/data/vaccinations/vaccinations-by-manufacturer.csv'
    vaccine_manf = pd.read_csv(manufacturer_url, error_bad_lines=False)
    vaccine_manf.to_csv(args.vax_bymanf, index=False)

    # Pull up-to-date statistics from data
    vaccine_nums['date'] = pd.to_datetime(vaccine_nums['date'])

    owid_stats["owid_most_recent_date"] = vaccine_nums['date'].max().strftime('%B %d, %Y').replace(' 0', ' ')

    vax_ww_data_latest = (
            vaccine_nums.dropna()
            >> ply.query("location == 'World'")
            >> ply.query("date == date.max()")
    ).to_dict(orient='list')

    owid_stats["owid_daily_rate"] = str(vax_ww_data_latest['daily_vaccinations_per_million'][0]) + \
                                    "per million"
    owid_stats["owid_total_vaccinations"] = billions(vax_ww_data_latest['total_vaccinations'][0])
    owid_stats["owid_worldwide_date"] = vax_ww_data_latest['date'][0].to_pydatetime().\
        strftime('%B %d, %Y').replace(' 0', ' ')

    # Identify number of vaccine manufacturers included in location totals (not the same as manufacturer-specific data)
    vaxCounts = set([item.strip() for countryList in
                    vaccine_locations["vaccines"].to_list()
                    for item in countryList.split(",")])
    owid_stats["owid_vaccine_counts"] = format(len(vaxCounts))

    # Transform list of vaccine candidate per iso code to list of ISO codes per vaccine candidate
    allVaxByCountry = dict(zip(vaccine_locations["iso_code"],
                               vaccine_locations["vaccines"]))
    owid_stats["owid_total_countries"] = str(len(allVaxByCountry))

    countryByVax = dict()
    for iso, vaccines in allVaxByCountry.items():
        for vax in vaccines.split(","):
            vax = vax.strip()
            countryCodes = countryByVax.get(vax, [])
            countryByVax[vax] = countryCodes + [iso]

    # Pull list of countries where specific vaccines have been authorized, as requested by authors
    for vaccine in ["Covaxin", "Sinovac"]:
        isos = countryByVax[vaccine]
        owid_stats[vaccine+"_country_count"] = str(len(isos))

        country_data = setup_geopandas()
        continents_df = (
                country_data[country_data['iso_a3'].isin(isos)]
                >> ply.select("continent")
                >> ply.distinct(["continent"])
        )
        continents = [value for row in sorted(continents_df.values.tolist()) for value in row]
        owid_stats[vaccine + "_continents"] = ', '.join(continents[:-1]) + ", and " + continents[-1]

    # Write output files
    write_JSON(countryByVax, args.country_byvax)
    write_JSON(owid_stats, args.output_json)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('output_json',
                        help='Path of the JSON file with extracted statistics',
                        type=str)
    parser.add_argument('country_byvax',
                        help='Path of the CSV file with the list of ISO codes \\'
                             ' per vaccine candidate',
                        type=str)
    parser.add_argument('vax_bymanf',
                        help='Path of the CSV file with the list of doses admin \\'
                             ' per vaccine (candidate)',
                        type=str)
    args = parser.parse_args()
    main(args)
