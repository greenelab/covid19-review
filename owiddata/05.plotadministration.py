import argparse
import pandas as pd
from jsonfn import *
from mapfn import *
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def getContinent(vaxPlatforms, countries_mapping):
    """Merge vaccine info with map info using a user-maintained list of iso codes
    associated with the place where the vaccine was developed"""
    print(vaxPlatforms[["Vaccine", "Company"]])
    exit(0)
    countryOfDev = pd.read_csv('owiddata/countryOfDev_OWID.csv')
    countryOfDev = countryOfDev.merge(vaxPlatforms, how = "outer",
                                      on=["OWID Nomenclature"])
    print(countryOfDev)
    return
    devCountryInfo = countryOfDev.merge(countries_mapping, how="left", on="iso_a3")

    # To do: if any VIPER vaccines are not in owiddata/countryOfDev.csv, open an issue
    # See https://medium.datadriveninvestor.com/github-issue-via-python-171c7fee0629

    return devCountryInfo

def getContinentText(devCountryInfo):
    """Generates dynamic text for each continent based on its vaccine development
    Input:
    Output: dictionary with continent: text"""
    sentences = dict()
    for continent in ["North America", "Asia", "Europe", "Oceania", "Africa", "South America"]:
        devVax = devCountryInfo[devCountryInfo["continent"] == continent]
        if len(devVax) == 0:
            sentences[continent] = "No approved vaccines have been developed in {0} [@url:https://covid19.trackvaccines.org]".format(continent)
        elif len(devVax) == 1:
            info = devVax.squeeze()
            sentences[continent] = "The only approved vaccine developed in {0} is {1}, which was developed by {2} in {3} [@url:https://covid19.trackvaccines.org].".\
                format(continent, info['Vaccine'], info['Company'], info['name'])
        else:
            # Need to construct the sentences to make them sound natural
            # To do this, we'll construct subclauses listing the details for each country,
            # like countryName (vaccine1, developer; vaccine2, developer)
            countryClauses = list()
            for country in devVax["name"].unique():
                countryVax = devVax[devVax["name"] == country].to_dict('index')
                countryItems = list()
                for record in countryVax.values():
                    countryItems.append(record["Vaccine"] + ", " + record["Company"])
                if country in ["United States of America", "Netherlands"]:
                    countryClauses.append("the " + country + " (" + "; ".join(countryItems) + ")")
                else:
                    countryClauses.append(country + " (" + "; ".join(countryItems) + ")")

            # Now construct the sentence from the clauses, with the last one prefaced by "and"
            sentences[continent] = \
                "Vaccines have been developed in {0} countries in {1}, including {2}, and {3}.".\
                    format(len(countryClauses),
                           continent,
                           ", ". join(countryClauses[:-1]),
                           countryClauses[-1])
    return sentences

def plotContinents(vaxPlatforms, countries_mapping, vaccine_manf):
    # Load OWID data and identify how many of each vaccine have been adminstered to date (it's cumulative)
    total_vaccinations = pd.DataFrame(
        vaccine_manf.groupby(['location', 'vaccine'])['total_vaccinations'].max())
    total_vaccinations.reset_index(inplace=True)

    # Add in the data about how many doses are in the primary series
    dosages = pd.read_csv("owiddata/owid-dosage.csv")
    total_vaccinations = total_vaccinations.merge(
        dosages[["OWID Nomenclature", "doses"]],
        how="inner", left_on='vaccine', right_on='OWID Nomenclature')
    # To Do: open issue if this data is missing

    # Add in the data about the platform used for the vaccine
    total_vaccinations = total_vaccinations.merge(
        vaxPlatforms[["OWID Nomenclature", "Platform"]],
        how="inner", on='OWID Nomenclature')

    # Add in the data about which continent each country is located on & other stats
    # Must be inner join to drop EU, which has no ISO code/Lowres data
    total_vaccinations = total_vaccinations.merge(countries_mapping[["name", "continent","pop_est", "iso_a3", "gdp_md_est"]],
                                                  how="inner", left_on='location', right_on='name')

    # Remove redundant columns for simplicity, add estimated stats
    total_vaccinations.drop(["OWID Nomenclature", "name"], axis=1, inplace=True)

    # Calculate the percentage of
    total_doses_admin = pd.DataFrame(
        total_vaccinations.groupby(
            ['vaccine'])['total_vaccinations'].sum())
    total_doses_admin.reset_index(inplace=True)
    total_doses_admin_continent = pd.DataFrame(
        total_vaccinations.groupby(
            ['vaccine', 'continent'])['total_vaccinations'].sum())
    total_doses_admin_continent.reset_index(inplace=True)
    print(total_doses_admin_continent)

    total_pop_continent = pd.DataFrame(
        countries_mapping.groupby(
            ['continent'])['pop_est'].sum())
    # Use only "countries" assigned to a continent to avoid redundancy
    total_pop_world = total_pop_continent["pop_est"].sum()
    perc_pop_continent = total_pop_continent / total_pop_world
    perc_pop_continent.reset_index(inplace=True)

    #for continent in countries_mapping["continent"].unique():
    return

def plotGDP():
    return

def main(args):
    # Load previously processed data
    owid_stats = load_JSON(args.update_json)
    vaxPlatforms = pd.read_csv(args.platform_types)
    vaxManf = pd.read_csv(args.vax_bymanf)
    countries_mapping = setup_geopandas()

    # Retrieve information about the country where vaccine was developed
    devCountryInfo = getContinent(vaxPlatforms,
                                  countries_mapping[["pop_est", "continent",
                                                     "name", "iso_a3", "gdp_md_est"]])
    print(devCountryInfo)
    exit(0)
    # Generate dynamic text based on which vaccines are available by continent
    sentences = getContinentText(devCountryInfo)
    for continent, sentence in sentences.items():
        owid_stats["viper_vax_dev_" + "_".join(continent.split())] = sentence

    #
    plotContinents(vaxPlatforms, countries_mapping, vaxManf)
    #countryByVax


    # The placeholder will be replaced by the actual SHA-1 hash in separate
    # script after the updated image is committed
    #owid_stats['owid_' + platformName + "_map"] = \
    #    f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.map_dir}/{platformName}.png'

    #with open(args.output_json, 'w') as out_file:
    #    json.dump(owid_stats, out_file, indent=2, sort_keys=True)
    #print(f'Wrote {args.output_json}')

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
    parser.add_argument('vax_bymanf',
                        help='Path of the CSV file with the list of doses admin \\'
                             ' per vaccine (candidate)',
                        type=str)
    args = parser.parse_args()
    main(args)
