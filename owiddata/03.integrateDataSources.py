import pandas as pd
from jsonFunctions import *
import argparse
from fuzzywuzzy import fuzz

def pair_datasource_names(viper_table, owid_names):
    """Match the vaccine names used in the two datasets
    Input: df generated from VIPER data, list of names from OWID data
    Returns: df including a column linking the datasets"""

    # Calculate match between the first two columns & the OWID names, generate
    # a heatmap comparing the index of the table to the list of OWID names
    name_match_ratio = dict()
    viperJointNames = viper_table.index.astype(str) + " " + viper_table["Company"]
    viperJointNames = viperJointNames.tolist()
    viper_names = dict(zip(viper_table.index, viperJointNames))

    for vname, vjointname in viper_names.items():
        name_match_ratio[vname] = [fuzz.partial_ratio(vjointname, oname)
                                   if oname != "ZF2001"
                                   else fuzz.partial_ratio(vjointname, "Zifivax* ZF2001 Anhui Zhifei Longcom")
                                   for oname in owid_names
                                   ]
    heatMap = pd.DataFrame.from_dict(name_match_ratio,
                                     orient="index",
                                     columns=owid_names)

    # Identify the best hit for each OWID vax name, since these are usually
    # a subset of the VIPER names
    owid_bestmatch = heatMap.idxmax(axis=0).to_dict() # row max
    viper_bestmatch = heatMap.idxmax(axis=1).to_dict()
    print(owid_bestmatch)
    unifiedNames = dict()
    for vname, oname in viper_bestmatch.items():
        if vname == owid_bestmatch[oname]:
            unifiedNames[vname] = oname
        elif oname == 
        else:
            unifiedNames[vname] = None

    viper_table['OWID Nomenclature'] = viper_table.index.map(unifiedNames)
    print("The following vaccines from VIPER were not matched to the OWID data:")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        null_data = viper_table[viper_table['OWID Nomenclature'].isnull()]
        print(null_data[["Company", "Platform", "URL"]])

    return viper_table

def main(args):
    # Load data from temporary files
    vaxPlatforms = pd.read_csv(args.platform_types, index_col="Vaccine")
    countryByVax = load_JSON(args.country_byvax)

    # Align the terminology used across the datasets
    vaxPlatforms = pair_datasource_names(vaxPlatforms, countryByVax.keys())

    # Add countries to vaccine platform info
    vaxPlatforms['countries'] = vaxPlatforms["OWID Nomenclature"].\
        map(countryByVax)

    # Write updated platform information to temporary file
    vaxPlatforms.to_csv(args.platform_types)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('platform_types',
                        help='Path of the CSV file with the vaccine to platform mapping',
                        type=str)
    parser.add_argument('country_byvax',
                        help='Path of the CSV file with the vaccine to platform mapping',
                        type=str)
    args = parser.parse_args()
    main(args)
