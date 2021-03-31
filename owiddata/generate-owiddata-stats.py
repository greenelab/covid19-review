import argparse
import datetime
import json
from datetime import date
import os
import pandas as pd

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
    # Import data from github.com/owid/covid-19-data
    owid_stats = dict()

    if('OWID_COMMIT_SHA' in os.environ):
        owid_stats['owid_commit_sha'] = os.environ['OWID_COMMIT_SHA']
    if('OWID_COMMIT_DATE' in os.environ):
        owid_stats['owid_commit_date'] = os.environ['OWID_COMMIT_DATE']
        owid_stats['owid_commit_date_pretty'] = convert_date(os.environ['OWID_COMMIT_DATE'])

    # Retrieve data from OWID
    locations_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/locations.csv'
    vaccine_locations = pd.read_csv(locations_url, error_bad_lines=False)

    numbers_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'
    vaccine_nums = pd.read_csv(numbers_url, error_bad_lines=False)

    manufacturer_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations-by-manufacturer.csv'
    vaccine_manf = pd.read_csv(manufacturer_url , error_bad_lines=False)

    # Pull up-to-date statistics from data
    vaccine_locations['last_observation_date'] = pd.to_datetime(vaccine_locations['last_observation_date'])
    vaccine_nums['date'] = pd.to_datetime(vaccine_nums['date'])
    vaccine_manf['date'] = pd.to_datetime(vaccine_manf['date'])

    owid_stats["most_recent_date"] = vaccine_nums['date'].max().strftime('%B %d, %Y').replace(' 0', ' ')

    owid_stats["total_vaccinations"] = str("{:,}".format(round(vaccine_nums[vaccine_nums["location"] ==
                                                          "World"].loc[vaccine_nums["date"] ==
                                                                       owid_stats["most_recent_date"],
                                                                       "total_vaccinations"].item()/1000000))) + \
                                       " million"
    owid_stats["daily_vax_rate"] = str("{:,}".format(round(vaccine_nums[vaccine_nums["location"] ==
                                                "World"].loc[vaccine_nums["date"] ==
                                                             owid_stats["most_recent_date"],
                                                             "daily_vaccinations_per_million"].item()))) + " per million"
    owid_stats["total_countries"] = format(vaccine_locations["location"].nunique())

    # Identify number of vaccine manufacturers included in location totals (not the same as manufacturer-specific data)
    owid_stats["vaccine_types"] = format(len(set([item.strip() for countryList in vaccine_locations["vaccines"].to_list() for
                                           item in countryList.split(",")])))

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
    args = parser.parse_args()
    main(args)
