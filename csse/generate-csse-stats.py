import argparse
import datetime
import json
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

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
    deaths_df = pd.read_csv(args.input_2019_deaths_csv)
    cases_df = pd.read_csv(args.input_2019_cases_csv)

    # The last column is the most recent date with data
    latest_deaths = deaths_df[deaths_df.columns[-1]]
    csse_stats['csse_date_pretty'] = convert_date(latest_deaths.name)
    total_deaths = latest_deaths.sum()
    csse_stats['csse_deaths'] = f'{total_deaths:,}'

    deaths_df = deaths_df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'])
    cumulative_deaths = deaths_df.sum(axis=0)

    latest_cases = cases_df[cases_df.columns[-1]]
    total_cases = latest_cases.sum()
    csse_stats['csse_cases'] = f'{total_cases:,}'

    cases_df = cases_df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'])
    cumulative_cases = cases_df.sum(axis=0)

    cumulative_deaths.index = pd.to_datetime(cumulative_deaths.index)
    cumulative_cases.index = pd.to_datetime(cumulative_cases.index)

    # Extract SARS (2002) statistics from WHO-scraped data on GitHub for comparison
    # Use date of first SARS case from WHO timeline to get days from first known case
    sars_df = pd.read_csv(args.input_2002_csv)
    sars_emergence_date = datetime.datetime.strptime("2002-11-16", '%Y-%m-%d')
    sars_daily = sars_df.groupby(by="Date").sum()
    sars_daily.index = pd.DatetimeIndex(sars_daily.index)
    sars_daily["Days"] = (sars_daily.index - sars_emergence_date).days
    sars_daily = sars_daily.rename({"Cumulative number of case(s)": "SARS Cases",
                       "Number of deaths": "SARS Deaths"}, axis=1)
    sars_daily = sars_daily.drop(["Number recovered"], axis=1)

    ## Fill in missing dates
    missing_dates = pd.Index(pd.date_range(start=sars_daily.index.min(),end=sars_daily.index.max()).\
        difference(pd.DatetimeIndex(sars_daily.index)))
    missing_df = pd.DataFrame(index=missing_dates, columns=sars_daily.columns)
    missing_df["Days"] = (missing_df.index - sars_emergence_date).days
    sars_daily = pd.concat([sars_daily, missing_df]).sort_index()
    sars_daily = sars_daily.astype(pd.Int64Dtype())
    sars_daily.interpolate(method="ffill", inplace=True)

    # Adjust COVID-19 data to use days since first known case instead of date
    # Date from https://www.businessinsider.com/coronavirus-patients-zero-contracted-case-november-2020-3
    covid_daily_dict = dict()
    covid_emergence_date = datetime.datetime.strptime("2019-11-17", '%Y-%m-%d')
    covid_daily_dict["Days"] = (cumulative_deaths.index - covid_emergence_date).days
    covid_daily_dict["COVID-19 Deaths"] = cumulative_deaths.values
    covid_daily_dict["COVID-19 Cases"] = cumulative_cases.values
    covid_daily = pd.DataFrame(covid_daily_dict)

    # Combine SARS and COVID-19 data in a single dataframe indexed by days from first known case
    daily_totals = pd.merge(left=covid_daily, right=sars_daily, how='left', on=["Days"])
    daily_totals['Days'] = daily_totals['Days'].astype(str).map(lambda x: x[:-5])
    daily_totals = daily_totals.set_index("Days")

    # Split daily_totals into cases and deaths to simplify plotting
    daily_cases = daily_totals[["SARS Cases", "COVID-19 Cases"]]
    daily_deaths = daily_totals[["SARS Deaths", "COVID-19 Deaths"]]

    # Set plot parameters
    title_size = 40
    legend_size = 25
    axis_size = 20
    tic_label_size = 15

    # Plot the daily totals
    sns.set_style("ticks")
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(35, 20))
    axes_list = axes.ravel()
    axis_info = {"title": {0: 'Cumulative Global Cases', 1: 'Cumulative Global Deaths',
                           2: 'Cumulative Global Cases (Zoomed)', 3: 'Cumulative Global Deaths (Zoomed)'},
                 "y_label": {0: 'Global Cases', 1: 'Global Deaths',
                             2: 'Global Cases', 3: 'Global Deaths'},
                 "data": {0: daily_cases, 1: daily_deaths, 2: daily_cases, 3: daily_deaths}}
    x_label = 'Days from First Known Case'

    for axis_num in [0, 1, 2, 3]:
        ax = axis_info["data"][axis_num].plot(kind='line', linewidth=2, ax=axes_list[axis_num])
        ax.set_title(axis_info["title"][axis_num], fontdict={'fontsize': title_size})
        ax.legend(loc='lower right', fontsize=legend_size)

        ax.tick_params(axis="both", labelsize=tic_label_size)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.minorticks_off()
        ax.grid(color="lightgray")

        ax.set_ylabel(axis_info["y_label"][axis_num], size=axis_size)
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        if axis_num == 2 or axis_num == 3:
            ax.set_ylim(bottom=0, top=10000)
        else:
            ax.set_ylim(bottom=0)

        ax.set_xlabel(x_label, size=axis_size, labelpad=20)
        ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    fig.subplots_adjust(hspace=0.3)
    plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=True)
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
    parser.add_argument('input_2019_deaths_csv',
                        help='Path of the JHU CSSE COVID-19 global deaths ' \
                        'input file',
                        type=str)
    parser.add_argument('input_2019_cases_csv',
                        help='Path of the JHU CSSE COVID-19 global cases ' \
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
