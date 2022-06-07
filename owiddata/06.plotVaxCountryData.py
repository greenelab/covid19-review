import argparse
import pandas as pd

def main(args):
    vaxManf = pd.read_csv(args.vax_bymanf)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('vax_bymanf',
                        help='Path of the CSV file with the list of doses admin \\'
                             ' per vaccine (candidate)',
                        type=str)
    args = parser.parse_args()
    main(args)
