import argparse
import datetime
import json
import os
import pandas as pd

# Inspired by https://github.com/greenelab/meta-review/blob/master/analyses/deep-review-contrib/03.contrib-stats.ipynb
def main(args):
    ''' Extract statistics from the JHU CSSE COVID-19 global deaths dataset'''
    csse_stats = dict()
    now = datetime.datetime.utcnow()
    csse_stats['csse_update_time_utc'] = now.isoformat()

    if('CSSE_COMMIT' in os.environ):
        csse_stats['csse_commit'] = os.environ['CSSE_COMMIT']

    deaths_df = pd.read_csv(args.input_file)
    # The last column is the most recent date with data
    latest_deaths = deaths_df[deaths_df.columns[-1]]
    csse_stats['csse_date_pretty'] = latest_deaths.name
    total_deaths = latest_deaths.sum()
    csse_stats['csse_deaths'] = f'{total_deaths:,}'

    deaths_df = deaths_df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'])
    print(deaths_df.columns)
    # TODO assert that all remaining columns are dates, convert date formatting
    cumulative_deaths = deaths_df.sum(axis=0)
    ax = cumulative_deaths.plot(kind='line')
    ax.set_ylabel('Global COVID-19 deaths')
    ax.figure.savefig('tmp.png', bbox_inches = "tight")
    ax.figure.savefig('tmp.svg', bbox_inches = "tight")

    # TODO generate a summary figure of deaths by date
    csse_stats['csse_deaths_figure'] = 'https://github.com/manubot/resources/raw/15493970f8882fce22bef829619d3fb37a613ba5/test/square.png'

    with open(args.output_file, 'w') as out_file:
        json.dump(csse_stats, out_file, indent=2, sort_keys=True)
    print(f'Wrote {args.output_file}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input_file',
                        help='JHU CSSE COVID-19 global deaths input file',
                        type=str)
    parser.add_argument('output_file',
                        help='JSON file with extracted statistics',
                        type=str)

    args = parser.parse_args()
    main(args)
