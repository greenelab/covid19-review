import argparse
import datetime
from datetime import date
import json
import matplotlib
import matplotlib.pyplot as plt
import os
import pandas as pd
import wget

def check_version(versionString, statsFile):
    """Check whether there are new updates to the CORD-19 dataset since the last time this script ran"""
    updateDate, updateSHA1 = versionString.split(".")
    prevSHA1 = 'N/A'
    if os.path.isfile(statsFile):
        prevRunInfo = json.load(open(statsFile, "r"))
        prevSHA1 = prevRunInfo["cord19_sha1"]

    if updateSHA1 == prevSHA1:
        exit("CORD-19 data is up to date")
    else:
        print(f"Downloading data from {updateDate} from https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html", flush=True)
        csvURL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/" + updateDate + "/metadata.csv"
        csvFile = wget.download(csvURL, out="CORD-19/metadata.csv")
        logURL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/" + updateDate + "/changelog"
        logFile = wget.download(logURL, out="CORD-19/changelog.txt")
        return csvFile, logFile, updateDate, updateSHA1

# Inspired by https://github.com/greenelab/meta-review/blob/master/analyses/deep-review-contrib/03.contrib-stats.ipynb
def main(args):
    # Set output dictionary
    cord19_stats = dict()

    # Check for updates (program will exit from function if no updates needed)
    csvFile, logFile, updateDate, sha1 = check_version(args.version_info, args.output_json)
    cord19_stats["cord19_update_date"] = updateDate
    cord19_stats["cord19_sha1"] = sha1

    print("Analyze CORD-19 data and generate outputs", flush=True)

    # Parse the log file ("changelog" on the website)
    textfile = open(logFile, "r")
    text = textfile.read()
    metadata_entries = text.split("---------------------------")

    corpus_size = dict()
    for entry in metadata_entries:
        components = entry.split("---")
        try:
            date = components[0].strip()
            summary_data = components[4].splitlines()
            total_rows = summary_data[1].split(":")[1].rstrip()
        except IndexError:
            # The first metadata entry is formatted differently than the others and throws an error
            summary_data = components[0].splitlines()
            date = summary_data[1].strip()
            total_rows = summary_data[4].split(" ")[-1].replace(")","")

        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError: # There is one malformed entry for 2020-09-11, this should also catch if more arise
            if date[0] == "s":
                date = date.split()[-1]
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
            else:
                print("malformed entry", date)
                exit(1)

        corpus_size[date] = int(total_rows)

    corpus_stats = pd.DataFrame.from_dict(corpus_size, orient="index", columns=['size'])

    # Parse the metadata file (csv formatted)
    paper_info = pd.read_csv(csvFile, usecols=[0,2,9])
    paper_info["publish_time"] = pd.to_datetime(paper_info["publish_time"])
    paper_info["source_x"] = paper_info["source_x"].str.lower()

    preprint_stats = dict()
    preprint_sources = ["arxiv", "medrxiv", "biorxiv"]
    for date, row in corpus_stats.iterrows():
        date_limits = '20200101 < publish_time < ' + date.__format__('%Y%m%d')
        recent_papers = paper_info.query(date_limits)
        counts = []
        for preprint_server in preprint_sources:
            preprints = recent_papers.source_x.str.contains(preprint_server)
            counts.append(int(sum(preprints)))
        preprint_stats[date] = counts

    preprint_df = pd.DataFrame.from_dict(preprint_stats, orient="index", columns = preprint_sources)
    preprint_df = preprint_df.rename(columns={"arxiv": "arXiv", "biorxiv": "bioRxiv", "medrxiv": "medRxiv"})

    # Get the most recent trial update
    most_recent_update = pd.to_datetime(corpus_stats.index).max()

    # Remove the leading zero of the day
    # Assumes the year will not begin with 0
    most_recent_update = most_recent_update.strftime('%Y-%m-%d').replace(' 0', ' ')
    cord19_stats['cord19_date_pretty'] = most_recent_update

    plt.rc('font', size=24)
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 12), constrained_layout=True, sharex=True)

    # Plot total number of manuscripts in CORD-19
    ax = corpus_stats.plot(kind='line', linewidth=5, ax=axes[0])
    ax.get_legend().remove()
    ax.set_ylabel('Total manuscripts')
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.set_ylim(bottom=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.minorticks_off()
    ax.grid(color="lightgray")

    # Plot breakdown of preprints, one line for each item in preprint_sources
    ax = preprint_df.plot(kind='line', linewidth=5, ax=axes[1])
    ax.set_ylabel('Preprints')
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.set_ylim(bottom=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.minorticks_off()
    ax.grid(color="lightgray")

    fig.savefig(args.output_figure + '.png', dpi=300, bbox_inches = "tight")
    fig.savefig(args.output_figure + '.svg', bbox_inches = "tight")

    print(f'Wrote {args.output_figure}.png and {args.output_figure}.svg')

    # The placeholder will be replaced by the actual SHA-1 hash in separate
    # script after the updated image is committed
    cord19_stats['cord19_figure'] = \
        f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.output_figure}.png'

    # Tabulate number of papers and preprints
    cord19_stats['cord19_total_pubs'] = \
        str(corpus_stats['size'].max())
    cord19_stats['cord19_total_preprints'] = \
        str(preprint_df.sum(axis=1).max())

    with open(args.output_json, 'w') as out_file:
        json.dump(cord19_stats, out_file, indent=2, sort_keys=True)
    print(f'Wrote {args.output_json}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('version_info',
                        help='Version info for the most recent update to the CORD-19 dataset ' \
                             'formatted as date[space]sha1',
                        type=str)
    parser.add_argument('output_json',
                        help='Path of the JSON file with extracted statistics',
                        type=str)
    parser.add_argument('output_figure',
                        help='Path of the output figure with publication ' \
                        'statistics without file type extension. Will be saved ' \
                        'as .png and .svg.',
                        type=str)
    args = parser.parse_args()
    main(args)
