import argparse
from jsonFunctions import load_JSON, write_JSON
import pandas as pd
import numpy as np
import plydata as ply
from mapFunctions import setup_geopandas, lowres_fix
import matplotlib as mpl
import matplotlib.pyplot as plt
from ast import literal_eval

def fix_owid_names(isoList):
    fixedlist = list()
    for iso in isoList:
        if iso[:4] == "OWID":
            if iso in ['OWID_ENG', 'OWID_SCT', 'OWID_WLS', 'OWID_NIR']:
                # These are subsets of data in iso code GBR
                continue
            elif iso == 'OWID_KOS':
                fixedlist.append("RKS")
            elif iso == "OWID_CYN":
                fixedlist.append("CYP")
            else:
                #would be great to raise issue since this requires debug
                print("Unknown country code: {iso}")
        else:
            fixedlist.append(iso)

def main(args):
    # Set up country mapping
    countries_mapping = setup_geopandas()

    # Load existing stats & grab scale for map from JSON
    owid_stats = load_JSON(args.update_json)

    # Load the integrated OWID/VIPER data
    vaxPlatforms = pd.read_csv(args.platform_types)

    # Count the number of vaccines of each type that OWID has data for
    # Then find max
    maxNumVax = (
            vaxPlatforms
            >> ply.call('.dropna', subset=['countries'])
            >> ply.group_by("Platform")
            >> ply.add_tally()
            >> ply.select("Platform", "Paper", "n")
            >> ply.group_by("Paper")
            >> ply.summarize_at('n', 'max')
    )
    maxNumVax.set_index("Paper", inplace=True)
    maxNumVax = maxNumVax.to_dict("index")

    for platform in set(vaxPlatforms["Platform"]):
        platformName = '_'.join(platform.split(' '))
        platformName = platformName.replace("-", "_")
        vaccines = vaxPlatforms[vaxPlatforms["Platform"] == platform].dropna()

        # This stat does not reveal the overall number of approved vaccines,
        # just the number tracked by OWID
        owid_stats["owid_" + platformName + "_count"] = \
            str(len(vaccines))
        if len(vaccines) == 0:
            owid_stats["owid_" + platformName + "_countries"] = str(len(vaccines))
            print("No data in OWID dataset for {}".format(platform))
            continue

        # Split lists in the "countries" column into individual ISO codes
        # and count how many unique countries appear
        listOfCodes= vaccines["countries"].apply(literal_eval)
        countries = pd.Series([iso for country_list in listOfCodes
                               for iso in country_list])
        owid_stats["owid_" + platformName + "_countries"] = str(len(countries.unique()))

        # Count how many times a country code appears across all vaccines
        # of this platform type
        vaxPresence = pd.DataFrame(countries.value_counts())
        vaxPresence.rename({0:platform}, axis=1, inplace=True)

        # Set the parameters color-coding the plots. Scale is the max candidates
        # adminstered across all vaccine types a) included in the OWID data, and
        # b) evaluated in the same paper as this vaccine
        paper = vaccines["Paper"].unique()[0]
        scale = maxNumVax[paper]['n'] + 1
        cmap = mpl.cm.Purples
        norm = mpl.colors.BoundaryNorm(np.arange(0, scale), cmap.N)

        # Use the vaxPresence data to set up the chloropeth
        mappingData = countries_mapping.merge(vaxPresence,
                                              how="left",
                                              right_index=True,
                                              left_on="iso_a3")
        mappingData[platform] = mappingData[platform].fillna(0)

        # plot data
        fig, ax = plt.subplots(1, 1, figsize=(12,10))
        ax.axis('off')
        countries_mapping.boundary.plot(ax=ax, edgecolor="black")

        mappingData.plot(column=platform, ax=ax,
                         legend=True, cmap=cmap, norm=norm,
                         legend_kwds={'shrink': 0.2})
        ax.set_title("Number of " + platform + " vaccines available worldwide")
        fig.tight_layout()

        plt.savefig(args.map_dir + "/" + platformName + '.png', dpi=1000, bbox_inches="tight")
        plt.savefig(args.map_dir + "/" + platformName + '.svg', bbox_inches="tight")

        print(f'Wrote {args.map_dir + "/" + platformName + ".png"} and '
              f'{args.map_dir + "/" + platformName + ".svg"}')

        # The placeholder will be replaced by the actual SHA-1 hash in separate
        # script after the updated image is committed
        owid_stats['owid_' + platformName + "_map"] = \
            f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.map_dir}/{platformName}.png'

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
    parser.add_argument('map_dir',
                        help='Path of directory containing image files with the vaccine distribution map images',
                        type=str)
    args = parser.parse_args()
    main(args)
