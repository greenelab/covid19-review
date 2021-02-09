import argparse
import datetime
import json
import os
import pandas as pd
import matplotlib

def convert_date(csse_date):
    '''Reformat CSSE style dates (MM/DD/YY) to Month DD, YYYY.
    Throws a ValueError if csse_date cannot be parsed as a date.
    '''
    # Remove the leading zero of the day
    # Assumes the year will not begin with 0
    return datetime.datetime.strptime(csse_date, '%m/%d/%y').strftime('%B %d, %Y').replace(' 0', ' ')

# Inspired by https://github.com/greenelab/meta-review/blob/master/analyses/deep-review-contrib/03.contrib-stats.ipynb
def main(args):
    '''Extract statistics from the JHU CSSE COVID-19 global deaths dataset'''
    csse_stats = dict()
    now = datetime.datetime.utcnow()
    csse_stats['csse_update_time_utc'] = now.isoformat()

    if('CSSE_COMMIT' in os.environ):
        csse_stats['csse_commit'] = os.environ['CSSE_COMMIT']
    deaths_df = pd.read_csv(args.input_csv)
    # The last column is the most recent date with data
    latest_deaths = deaths_df[deaths_df.columns[-1]]
    csse_stats['csse_date_pretty'] = convert_date(latest_deaths.name)
    total_deaths = latest_deaths.sum()
    csse_stats['csse_deaths'] = f'{total_deaths:,}'

    deaths_df = deaths_df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'])
    
    cumulative_deaths = deaths_df.sum(axis=0)
    cumulative_deaths.index = pd.to_datetime(cumulative_deaths.index)
    
    ax = cumulative_deaths.plot(kind='line', linewidth=2)
    ax.set_ylabel('Global COVID-19 deaths')
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.set_ylim(bottom=0)    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.minorticks_off()
    ax.grid(color="lightgray")
    
    ax.figure.savefig(args.output_figure + '.png', dpi=300, bbox_inches = "tight")
    ax.figure.savefig(args.output_figure + '.svg', bbox_inches = "tight")


    print(f'Wrote {args.output_figure}.png and {args.output_figure}.svg')

    # The placeholder will be replaced by the actual SHA-1 hash in separate
    # script after the updated image is committed
    csse_stats['csse_deaths_figure'] = \
        f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.output_figure}.png'

    with open(args.output_json, 'w') as out_file:
        json.dump(csse_stats, out_file, indent=2, sort_keys=True)
    print(f'Wrote {args.output_json}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input_csv',
                        help='Path of the JHU CSSE COVID-19 global deaths ' \
                        'input file',
                        type=str)
    parser.add_argument('output_json',
                        help='Path of the JSON file with extracted statistics',
                        type=str)
    parser.add_argument('output_figure',
                        help='Path of the output figure with daily global ' \
                        'deaths without file type extension. Will be saved ' \
                        'as .png and .svg.',
                        type=str)

    args = parser.parse_args()
    main(args)
