import argparse
import pandas as pd
from jsonFunctions import load_JSON, write_JSON
from mapFunctions import setup_geopandas
from plotnine import ggplot, aes, geom_point, geom_smooth, geom_bar, ggtitle, ylab, xlab
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def evaluateDistribution(vaxPlatforms, countries_mapping, vaccine_manf):
    # Load OWID data and identify how many of each vaccine have been adminstered to date (it's cumulative,
    # so only need the most recent/max entry)
    total_vaccinations = pd.DataFrame(
        vaccine_manf.groupby(['location', 'vaccine'])['total_vaccinations'].max())
    total_vaccinations.reset_index(inplace=True)
    total_vaccinations.rename(columns={"location":"country_name",
                                       "vaccine":"OWID Nomenclature"},
                              inplace=True)

    # Add in the data about the platform used for the vaccine
    total_vaccinations = total_vaccinations.merge(
        vaxPlatforms[["OWID Nomenclature", "Platform"]],
        how="inner", on='OWID Nomenclature')

    # Add in the data about which continent each country is located on & other stats
    # Must be inner join to drop EU, which has no ISO code/Lowres data
    total_vaccinations = total_vaccinations.merge(countries_mapping[["name", "continent",
                                                                     "pop_est", "iso_a3",
                                                                     "gdp_md_est"]],
                                                  how="inner", left_on='country_name', right_on='name')

    # Remove redundant column for simplicity
    total_vaccinations.drop("name", axis=1, inplace=True)

    plotTypeGDP(total_vaccinations)
    plotDistContinent(total_vaccinations, countries_mapping)

def plotTypeGDP(total_vaccinations):
    by_platform = pd.DataFrame(
        total_vaccinations.groupby(
            ['country_name', 'Platform', 'pop_est', 'gdp_md_est'])['total_vaccinations'].sum())
    by_platform.reset_index(inplace=True)
    p = (ggplot(by_platform, aes('gdp_md_est/1000', 'total_vaccinations/1000000', color='Platform'))
         + geom_point()
         + geom_smooth(method="auto", se=True, fullrange=False, level=0.95)
         + ggtitle("Administration of COVID-19 Vaccine Doses")
         + xlab("National GDP (Billions of Dollars)")
         + ylab("Doses Adminmistered (Millions)")
         )
    p.save(filename='owiddata/OWID_doseTypebyGDP.png', height=4, width=7, units='in', dpi=1000, verbose = False)
    print(f'Wrote {args.doses_scatterplot}')

def plotDistContinent(total_vaccinations, countries_mapping):
    # Calculate statistics about the doses of each vaccine administered

    total_doses_admin = pd.DataFrame(
        total_vaccinations.groupby(
            ['Platform', 'OWID Nomenclature', 'continent'])['total_vaccinations'].sum())
    total_doses_admin.reset_index(inplace=True)

    total_pop_continent = pd.DataFrame(
        countries_mapping.groupby(
            ['continent'])['pop_est'].sum())

    doses_pop_continent = total_doses_admin.merge(total_pop_continent, how="inner", on='continent')
    doses_pop_continent["per_capita"] = doses_pop_continent["total_vaccinations"] / doses_pop_continent["pop_est"]
    doses_pop_continent.sort_values(by=['Platform'])

    # If the dosage number is too low, the bars aren't legible, so setting min at 1M
    p = (ggplot(doses_pop_continent[doses_pop_continent["total_vaccinations"] > 1000000],
                aes(x='OWID Nomenclature', y='per_capita', fill="continent"))
         + geom_bar(stat="identity") # position="dodge")
         + ggtitle("Administered COVID-19 Vaccine Doses (OWID)")
         + ylab("Doses Adminmistered Per Capita")
         + xlab("Vaccine Manufacturer")
         )

    p.save(filename='owiddata/OWID_dosesByContinent.png', height=4, width=14, units='in', dpi=1000, verbose = False)
    print(f'Wrote {args.doses_bargraph}')

def main(args):
    # Load previously processed data
    owid_stats = load_JSON(args.update_json)
    vaxPlatforms = pd.read_csv(args.platform_types)
    vaxManf = pd.read_csv(args.vax_bymanf)
    countries_mapping = setup_geopandas()

    # Call plotting functions
    evaluateDistribution(vaxPlatforms, countries_mapping, vaxManf)

    # The placeholder will be replaced by the actual SHA-1 hash in separate
    # script after the updated image is committed
    owid_stats['owid_doses_bargraph'] = \
    f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.doses_bargraph}'
    owid_stats['owid_doses_scatterplot'] = \
    f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.doses_scatterplot}'
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
    parser.add_argument('vax_bymanf',
                        help='Path of the CSV file with the list of doses admin \\'
                             ' per vaccine (candidate)',
                        type=str)
    parser.add_argument('doses_bargraph',
                        help='PNG image showing doses per capita for each manufacturer by continent',
                        type=str)
    parser.add_argument('doses_scatterplot',
                        help='PNG image showing relationship between GDP and doses per capita by platform',
                        type=str)
    args = parser.parse_args()
    main(args)
