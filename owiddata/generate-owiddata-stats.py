import argparse
import datetime
import json
import os
import pandas as pd
import geopandas
import pycountry
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

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

    # Set the parameters color-coding the plots. Scale is the max candidates adminstered across all vaccine types.
    scale = max(vaxPlatforms["Type"].value_counts())
    cmap = mpl.cm.Purples
    norm = mpl.colors.BoundaryNorm(np.arange(0, scale + 1), cmap.N)

    # Check that platform information is present (needs to be manually determined and input in vaccine_platforms.csv
    missingInfo = [vax for vax in vaxTypes if vax not in vaxPlatforms.index]
    if len(missingInfo) > 0:
        exit("Missing platform information for " + ", ".join(missingInfo))

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

    for platform in set(list(vaxPlatforms["Type"])):
        fig, ax = plt.subplots(1, 1, figsize=(6,4))
        ax.axis('off')

        vaccines = vaxPlatforms[vaxPlatforms["Type"] == platform]
        countries = [iso for country_list in vaccines["countries"] for iso in country_list]
        counts = dict()
        for iso in countries:
            runningTot = counts.get(iso, 0)
            counts[iso] = runningTot + 1

        vaxPresence = pd.DataFrame.from_dict(counts, orient="index",
                                             columns=[platform])
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

        filename = '_'.join(platform.split(' '))
        plt.savefig(args.map_dir + "/" + filename + '.png', dpi=300, bbox_inches="tight")
        plt.savefig(args.map_dir + "/" + filename + '.svg', bbox_inches="tight")

        print(f'Wrote {args.map_dir + "/" + filename + ".png"} and '
              f'{args.map_dir + "/" + filename + ".svg"}')

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
