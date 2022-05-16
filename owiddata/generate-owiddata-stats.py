import argparse
import json
import pandas as pd
import geopandas
import matplotlib as mpl
import matplotlib.pyplot as plt


def main(args):
    # geopandas init moved to 04

    # code here moved to 01

    # code here moved to 02

    # map init moved to 04

    # moved to 01 - countriesbyvax

    # moved to 03


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
