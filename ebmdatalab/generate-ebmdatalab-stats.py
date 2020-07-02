import argparse
import datetime
import json
import os
import pandas as pd
import matplotlib

def convert_date(git_date):
    '''Reformat git commit style datetimes (ISO 8601) to Month DD, YYYY.
    Throws a ValueError if git_date cannot be parsed as an ISO 8601 datetime.
    '''
    # 'Z' indicates Coordinated Universal Time (UTC)
    # Replace with '+00:00', which is the UTC representation recognized
    # by the parser
    # https://en.wikipedia.org/wiki/ISO_8601#Coordinated_Universal_Time_(UTC)
    git_date = git_date.replace('Z', '+00:00')
    
    # Remove the leading zero of the day
    # Assumes the year will not begin with 0
    return datetime.datetime.fromisoformat(git_date).strftime('%B %d, %Y').replace(' 0', ' ')

# Inspired by https://github.com/greenelab/meta-review/blob/master/analyses/deep-review-contrib/03.contrib-stats.ipynb
def main(args):
    '''Extract statistics from the EBM Data Lab COVID-19 TrialsTracker dataset'''
    ebm_stats = dict()
    now = datetime.datetime.utcnow()
    ebm_stats['ebm_update_time_utc'] = now.isoformat()

    if('EBM_COMMIT_SHA' in os.environ):
        ebm_stats['ebm_commit_sha'] = os.environ['EBM_COMMIT_SHA']
    if('EBM_COMMIT_DATE' in os.environ):
        ebm_stats['ebm_commit_date'] = os.environ['EBM_COMMIT_DATE']
        ebm_stats['ebm_commit_date_pretty'] = convert_date(os.environ['EBM_COMMIT_DATE'])

    trials_df = pd.read_json(args.input_json, orient='split')
    # Use header from the HTML table
    # https://github.com/ebmdatalab/covid_trials_tracker-covid/blob/6c2b9965b170aa6c53e7f755692a4f221de694bf/docs/results/index.html#L56
    # Those are the same order but different names from the original dataframe
    # https://github.com/ebmdatalab/covid_trials_tracker-covid/blob/6c2b9965b170aa6c53e7f755692a4f221de694bf/notebooks/diffable_python/ictrp_data_handling.py#L544
    header = ['index', 'trial_id', 'registry', 'registration_date', 'start_date', \
              'retrospective_registration', 'sponsor', 'recruitment_status', \
              'phase', 'study_type', 'countries', 'title', 'study_category', \
              'intervention', 'intervention_list', 'enrollment', \
              'primary_completion_date', 'full_completion_date', 'registy_url', \
              'results_type', 'results_published_date', 'results_url', 'last_updated', \
              'cross_registration']
    assert (len(header) == len(trials_df.columns))
    trials_df.columns = header
    trials_df = trials_df.set_index('index')
    
    ebm_stats['ebm_trials'] = len(trials_df.index)
    
    # Get the most recent trial update
    most_recent_update = pd.to_datetime(trials_df['last_updated']).max()
    # Remove the leading zero of the day
    # Assumes the year will not begin with 0
    most_recent_update = most_recent_update.strftime('%B %d, %Y').replace(' 0', ' ')
    ebm_stats['ebm_date_pretty'] = most_recent_update
    
    with open(args.output_json, 'w') as out_file:
        json.dump(ebm_stats, out_file, indent=2, sort_keys=True)
    print(f'Wrote {args.output_json}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input_json',
                        help='Path of the EBM Data Lab COVID-19 TrialsTracker ' \
                        'input JSON file',
                        type=str)
    parser.add_argument('output_json',
                        help='Path of the JSON file with extracted statistics',
                        type=str)
    parser.add_argument('output_figure',
                        help='Path of the output figure with clinical trials ' \
                        'statistics without file type extension. Will be saved ' \
                        'as .png and .svg.',
                        type=str)

    args = parser.parse_args()
    main(args)
