import argparse
import datetime
import json
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

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
    deaths_df = pd.read_csv(args.input_2019_csv)
    # The last column is the most recent date with data
    latest_deaths = deaths_df[deaths_df.columns[-1]]
    csse_stats['csse_date_pretty'] = convert_date(latest_deaths.name)
    total_deaths = latest_deaths.sum()
    csse_stats['csse_deaths'] = f'{total_deaths:,}'

    deaths_df = deaths_df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'])
    cumulative_deaths = deaths_df.sum(axis=0)

    cumulative_deaths.index = pd.to_datetime(cumulative_deaths.index)

    # Extract SARS (2002) statistics from WHO-scraped data on GitHub
    sars_df = pd.read_csv(args.input_2002_csv)

    # Date from WHO timeline
    sars_emergence_date = datetime.datetime.strptime("2002-11-16", '%Y-%m-%d')
    sars_daily = sars_df.groupby(by="Date").sum()
    sars_daily["Days"] = pd.DatetimeIndex(sars_daily.index) - sars_emergence_date
    sars_daily.rename(columns={"Number of deaths": "SARS Deaths"}, inplace=True)
    print(sars_daily["SARS Deaths"].max())

    # reformat date to just month and day
    covid_daily_dict=dict()
    # Date from https://www.businessinsider.com/coronavirus-patients-zero-contracted-case-november-2020-3
    covid_emergence_date = datetime.datetime.strptime("2019-11-17", '%Y-%m-%d')
    covid_daily_dict["Days"] = cumulative_deaths.index - covid_emergence_date
    covid_daily_dict["COVID-19 Deaths"] = cumulative_deaths.values
    covid_daily = pd.DataFrame(covid_daily_dict)

    daily_totals = pd.merge(left=covid_daily, right=sars_daily, how='left', on=["Days"])
    daily_totals = daily_totals.drop(["Cumulative number of case(s)", "Number recovered"], axis=1)
    daily_totals['Days'] = daily_totals['Days'].astype(str).map(lambda x: x[:-5])
    daily_totals = daily_totals.set_index("Days")

    # Plot the daily totals
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(20, 12), constrained_layout=True)
    ax = daily_totals.plot(kind='line', linewidth=2, ax=axes[0])
    ax.set_xlabel('Days from First Known Case')
    ax.set_ylabel('Global Deaths')
    ax.set_title("Global Deaths from SARS versus COVID-19")
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.set_ylim(bottom=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.minorticks_off()
    ax.grid(color="lightgray")

    # Make a function to smoothe the SARS data
    daily_totals_sars = daily_totals.loc[daily_totals['SARS Deaths'].notna()]
    smoothe_sars = make_interp_spline(daily_totals_sars.index, daily_totals_sars["SARS Deaths"])

    # Select all days for which we have SARS numbers reported
    first_sars_report = int(daily_totals.loc[daily_totals['SARS Deaths'].notna()].index.min())
    last_sars_report = int(daily_totals.loc[daily_totals['SARS Deaths'].notna()].index.max())
    sars_day_range = range(first_sars_report, last_sars_report + 1)

    # Smoothe data in range where SARS numbers were reported
    sars_smoothed = pd.DataFrame(smoothe_sars(sars_day_range), index = sars_day_range,
                                 columns=["SARS Deaths"])
    #daily_totals_smoothed = daily_totals[(pd.to_numeric(daily_totals.index) < first_sars_report)]
    #daily_totals_smoothed = daily_totals_smoothed.append(sars_smoothed.merge(daily_totals["COVID-19 Deaths"],
    #                                                                         left_index = sars_smoothed.index,
    #                                                                         right_index=daily_totals.index))
    #daily_totals_smoothed = daily_totals_smoothed.append(daily_totals[(pd.to_numeric(daily_totals.index) > last_sars_report)])
    daily_totals_smoothed = daily_totals.update(sars_smoothed)
    daily_totals_smoothed = pd.merge(sars_smoothed, daily_totals, how="outer")
    print(daily_totals_smoothed)
    print(daily_totals)

    # Plot the second panel
    ax = daily_totals.plot(kind='line', linewidth=2, ax=axes[1])
    ax.set_xlabel('Days from First Known Case')
    ax.set_ylabel('Global Deaths')
    ax.set_title("Global Deaths from SARS (Zoomed)")
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.set_ylim(bottom=0, top=1000)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.minorticks_off()
    ax.grid(color="lightgray")

    ax.figure.savefig(args.output_figure + '.png', dpi=300, bbox_inches="tight")
    ax.figure.savefig(args.output_figure + '.svg', bbox_inches="tight")

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
    parser.add_argument('input_2019_csv',
                        help='Path of the JHU CSSE COVID-19 global deaths ' \
                        'input file',
                        type=str)
    parser.add_argument('input_2002_csv',
                        help='Path of the Kaggle SARS global deaths ' \
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
