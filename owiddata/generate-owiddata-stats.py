import argparse
import json
import pandas as pd
import geopandas
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

def main(args):
    # Set up country mapping
    countries_mapping = setup_geopandas()

    # Create dictionary that will be exported as JSON
    #owid_stats = dict()

    # code here moved to 01

    # code here moved to 02

    # Set the parameters color-coding the plots. Scale is the max candidates adminstered across all vaccine types.
    scale = max(numVax)
    cmap = mpl.cm.Purples
    norm = mpl.colors.BoundaryNorm(np.arange(0, scale + 1), cmap.N)

    # moved to 01 - countriesbyvax

    # moved to 03

    for platform in set(vaxPlatforms["Platform"]):
        platformName = '_'.join(platform.split(' '))
        platformName = platformName.replace("-", "_")
        owid_stats["owid_" + platformName + "_count"] = \
            len(vaxPlatforms[vaxPlatforms["Platform"] == platform])

        fig, ax = plt.subplots(1, 1, figsize=(6,4))
        ax.axis('off')

        vaccines = vaxPlatforms[vaxPlatforms["Platform"] == platform].dropna()
        countries = [iso for country_list in vaccines["countries"]
                     for iso in country_list]
        counts = dict()
        for iso in countries:
            runningTot = counts.get(iso, 0)
            counts[iso] = runningTot + 1

        vaxPresence = pd.DataFrame.from_dict(counts, orient="index",
                                             columns=[platform])
        owid_stats["owid_" + platformName + "_countries"] = len(vaxPresence)
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

        plt.savefig(args.map_dir + "/" + platformName + '.png', dpi=300, bbox_inches="tight")
        plt.savefig(args.map_dir + "/" + platformName + '.svg', bbox_inches="tight")

        print(f'Wrote {args.map_dir + "/" + platformName + ".png"} and '
              f'{args.map_dir + "/" + platformName + ".svg"}')

        # The placeholder will be replaced by the actual SHA-1 hash in separate
        # script after the updated image is committed
        owid_stats['owid_' + platformName + "_map"] = \
            f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.map_dir}/{platformName}.png'

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
