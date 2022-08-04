import argparse
import pandas as pd
from jsonFunctions import load_JSON, write_JSON
from mapFunctions import setup_geopandas

def getContinent(vaxPlatforms, countries_mapping):
    """Merge vaccine info with map info using a user-maintained list of iso codes
    associated with the place where the vaccine was developed"""
    countryOfDev = pd.read_csv('owiddata/countryOfDev_OWID.csv')
    countryOfDev = countryOfDev.merge(vaxPlatforms, how = "outer",
                                      on=["OWID Nomenclature"])
    devCountryInfo = countryOfDev.merge(countries_mapping, how="left", left_on="Developer_ISO",
                                        right_on="iso_a3")

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
            # Need to construct a natural-sounding sentence
            # To do this, we'll construct subclauses listing the details for each country,
            # as: countryName (vaccine1, developer1; vaccine2, developer2)
            countryClauses = list()
            for country in devVax["name"].unique():
                # This creates a dictionary with the key as the row index (not ideal)
                countryVax = devVax[devVax["name"] == country].to_dict('index')

                # Process each vaccine record for this country
                countryItems = list()
                for record in countryVax.values():
                    countryItems.append("{0}, {1}".format(record['Vaccine'],
                                                              record['Company']))

                # Add context to make the list fit naturally into a sentence
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

def main(args):
    # Load previously processed data
    owid_stats = load_JSON(args.update_json)
    vaxPlatforms = pd.read_csv(args.platform_types)
    countries_mapping = setup_geopandas()

    # Retrieve information about the country where vaccine was developed
    devCountryInfo = getContinent(vaxPlatforms,
                                  countries_mapping[["pop_est", "continent",
                                                     "name", "iso_a3", "gdp_md_est"]])
    # Generate dynamic text based on which vaccines are available by continent
    sentences = getContinentText(devCountryInfo)

    for continent, sentence in sentences.items():
        owid_stats["viper_vax_dev_" + "_".join(continent.split())] = sentence
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
