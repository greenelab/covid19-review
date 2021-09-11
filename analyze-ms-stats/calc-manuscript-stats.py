import json
import pandas as pd
import matplotlib
import argparse
import time
from pathlib import Path
import multiprocessing
import subprocess

def analyze_commit(commit):
    """Access files and data in variables.json associated with each commit
    Accepts commit ID as string
    Returns list of 5 statistics"""

    try:
        variablesCommand = "git show " + commit + ":./variables.json"
        variables = json.loads(subprocess.getoutput(variablesCommand))
    except json.decoder.JSONDecodeError:
        exit(commit + " not found")

    date = variables['pandoc']['date-meta']
    clean_date = variables['manubot']['date']
    num_authors = len(variables['manubot']['authors'])
    word_count = variables['manubot']['manuscript_stats']['word_count']

    # Access files and data in references.json associated with each commit
    referencesCommand = "git show " + commit + ":./references.json"
    references = json.loads(subprocess.getoutput(referencesCommand))
    num_ref = len(references)

    return ({"stats_date": date,
             "stats_clean_date": clean_date,
             "stats_num_authors": num_authors,
             "stats_num_words": word_count,
             "stats_num_references": num_ref})

def main(args):
    '''Extract statistics from the output branch log'''

    print("Using {0} CPUs".format(multiprocessing.cpu_count()))

    # Read in list of all commits on this branch
    with open(args.commit_list, "r") as commitFile:
        commits = [c.strip() for c in commitFile.read().splitlines()]

    # If this analysis has been run before, load in the list of commits analyzed
    # and only analyze new commits
    # Assumes no commits will be added retrospectively (to take advantage of linearity)
    priorData = None
    if Path(args.output_table).is_file():
        priorData = pd.read_csv(args.output_table)
        oldCommits = priorData["commit"].tolist()
        priorData = priorData.set_index("commit")

        if len(commits) > len(oldCommits):
            start_old = commits.index(oldCommits[0])
            commits = commits[:start_old]
            print("{0} new commits".format(len(commits)))
        else:
            exit("No new commits")

    # Access the variables.json and references.json files associated with each commit and store in dictionary
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        commitData = dict(zip(commits, pool.map(analyze_commit, commits)))
        pool.close()
        pool.join()

    # Turn commitData to df, then flip to be in chronological order
    growthData = pd.DataFrame.from_dict(commitData, orient="index")
    growthData = growthData.rename(columns={"stats_date": "Date",
                               "stats_clean_date": "Clean_date",
                               "stats_num_authors": "Authors",
                               "stats_num_words": "Word Count",
                               "stats_num_references": "References"})
    # Append onto table of previous commit data, if this exists
    if priorData is not None:
        growthData = growthData.append(priorData)

    # Cache commit data for future updates
    growthData.to_csv(args.output_table, index_label="commit")
    print('Wrote {}'.format(args.output_table))

    # Prepare data to graph
    graphData = growthData.set_index("Date")
    graphData = graphData[::-1]

    # Plot the data
    axes = graphData.plot(kind='line', linewidth=2, subplots=True)
    for ax in axes:
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda x, p: format(int(x), ',')))
        ax.set_ylabel('Count')
        ax.set_ylim(bottom=0)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.minorticks_off()
        ax.grid(color="lightgray")

    ax.figure.savefig(args.output_figure + '.png', dpi=300, bbox_inches="tight")
    ax.figure.savefig(args.output_figure + '.svg', bbox_inches="tight")

    print('Wrote {0}.png and {1}.svg'.format(args.output_figure, args.output_figure))

    # Write json output file
    manuscript_stats = commitData[commits[0]]
    for item in ["stats_num_authors", "stats_num_words", "stats_num_references"]:
        manuscript_stats[item] = str(manuscript_stats[item])
    with open(args.output_json, 'w') as out_file:
        json.dump(manuscript_stats, out_file, indent=2, sort_keys=True)
    print('Wrote {0}'.format(args.output_json))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('commit_list',
                        help='File containing a list of all commits on output branch, one per line',
                        type=str)
    parser.add_argument('output_json',
                        help='Path of the JSON file with extracted statistics',
                        type=str)
    parser.add_argument('output_figure',
                        help='Path of the output figure for manuscript ' \
                             'statistics without file type extension. Will be saved ' \
                             'as .png and .svg.',
                        type=str)
    parser.add_argument('output_table',
                        help='Path of the output table used to generate ' \
                             'figures ',
                        type=str)
    args = parser.parse_args()
    main(args)
