import pandas as pd
import os
import datetime
import argparse
from jsonFunctions import *
import plydata as ply
import numpy as np

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

    # Retrieve data from OWID
    locations_url = f'https://raw.githubusercontent.com/owid/covid-19-data/{commit}/public/data/vaccinations/locations.csv'
    vaccine_locations = pd.read_csv(locations_url, error_bad_lines=False)

    numbers_url = f'https://raw.githubusercontent.com/owid/covid-19-data/{commit}/public/data/vaccinations/vaccinations.csv'
    vaccine_nums = pd.read_csv(numbers_url, error_bad_lines=False)

    manufacturer_url = f'https://raw.githubusercontent.com/owid/covid-19-data/{commit}/public/data/vaccinations/vaccinations-by-manufacturer.csv'
    vaccine_manf = pd.read_csv(manufacturer_url, error_bad_lines=False)
    vaccine_manf.to_csv(args.vaccine_manf)

    # Pull up-to-date statistics from data
    vaccine_nums['date'] = pd.to_datetime(vaccine_nums['date'])

    owid_stats["owid_most_recent_date"] = vaccine_nums['date'].max().strftime('%B %d, %Y').replace(' 0', ' ')

    # To do: Add a check to make sure < 1 trillion and open issue if not
    owid_stats["owid_total_vaccinations"] = billions(
        (vaccine_nums
            >> ply.query("location == 'World'")
            >> ply.query("date == date.max()")
            >> ply.pull("total_vaccinations")
    ).item())

    # Identify number of vaccine manufacturers included in location totals (not the same as manufacturer-specific data)
    vaxCounts = set([item.strip() for countryList in
                    vaccine_locations["vaccines"].to_list()
                    for item in countryList.split(",")])
    owid_stats["owid_vaccine_counts"] = format(len(vaxCounts))

    # Transform list of vaccine candidate per iso code to list of ISO codes per vaccine candidate
    allVaxByCountry = dict(zip(vaccine_locations["iso_code"],
                               vaccine_locations["vaccines"]))
    countryByVax = dict()
    for iso, vaccines in allVaxByCountry.items():
        for vax in vaccines.split(","):
            vax = vax.strip()
            countryCodes = countryByVax.get(vax, [])
            countryByVax[vax] = countryCodes + [iso]

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
    parser.add_argument('vaccine_manf',
                        help='Path of the CSV file describing which vaccines have been \\'
                             ' administered in each country',
                        type=str)
    args = parser.parse_args()
    main(args)
