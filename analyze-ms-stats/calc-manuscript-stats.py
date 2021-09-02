import json
import subprocess
import pandas as pd
import matplotlib
import argparse
import multiprocessing

def analyze_commit(commit):
    """Access files and data in variables.json associated with each commit
    Accepts commit ID # as string
    Returns list of 5 statistics"""

    variablesCommand = "git show " + commit + ":./variables.json"
    variables = json.loads(subprocess.getoutput(variablesCommand))

    date = variables['pandoc']['date-meta']
    clean_date = variables['manubot']['date']
    num_authors = len(variables['manubot']['authors'])
    word_count = variables['manubot']['manuscript_stats']['word_count']

    # Access files and data in references.json associated with each commit
    referencesCommand = "git show " + commit + ":./references.json"
    references = json.loads(subprocess.getoutput(referencesCommand))
    num_ref = len(references)

    return([date, clean_date, num_authors, word_count, num_ref])

def main(args):
    '''Extract statistics from the output branch log'''

    # Access the variables.json and references.json files associated with each commit and store in dictionary
    with open(args.commit_list, "r") as commitFile:
        commits = [c.strip() for c in commitFile.read().splitlines()]
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        commitData = dict(zip(commits, pool.map(analyze_commit, commits)))
        pool.close()
        pool.join()

    # Convert dictionary to dataframe & flip index to be chronological
    growthdata = pd.DataFrame.from_dict(commitData, orient="index",
                                        columns=["Date", "clean_date", "Authors", "Word Count", "References"])
    manuscript_stats = growthdata.iloc[0].to_dict()
    for item in ["Authors", "Word Count", "References"]:
        manuscript_stats[item] = str(manuscript_stats[item])
    growthdata = growthdata[::-1]
    growthdata = growthdata.set_index("Date")

    # Plot the data
    axes = growthdata.plot(kind='line', linewidth=2, subplots=True)
    for ax in axes:
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda x, p: format(int(x), ',')))
        ax.set_ylabel('Count')
        ax.set_ylim(bottom=0)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.minorticks_off()
        ax.grid(color="lightgray")

    ax.figure.savefig(args.output_figure + '.png', dpi=300, bbox_inches = "tight")
    ax.figure.savefig(args.output_figure + '.svg', bbox_inches = "tight")

    print(f'Wrote {args.output_figure}.png and {args.output_figure}.svg')

    # Write json output file
    with open(args.output_json, 'w') as out_file:
        json.dump(manuscript_stats, out_file, indent=2, sort_keys=True)
    print(f'Wrote {args.output_json}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('commit_list',
                        help='List of all commits on output branch, one per line',
                        type=str)
    parser.add_argument('output_json',
                        help='Path of the JSON file with extracted statistics',
                        type=str)
    parser.add_argument('output_figure',
                        help='Path of the output figure for manuscript ' \
                        'statistics without file type extension. Will be saved ' \
                        'as .png and .svg.',
                        type=str)
    args = parser.parse_args()
    main(args)
