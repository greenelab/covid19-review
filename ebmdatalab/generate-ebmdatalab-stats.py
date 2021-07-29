import argparse
import datetime
import json
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import geopandas
import pycountry

from manubot.cite.citekey import url_to_citekey
from manubot.cite.doi import get_short_doi_url

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

def extract_citekey(results_url):
    '''Extract a Manubot citation key from the results URL. Uses short DOI if
    citekey is a DOI and contains parentheses.'''
    citekey = url_to_citekey(results_url)
    # citekey typically in the form doi:10.1101/2020.05.31.20114520 or
    # url:https://clinicaltrials.gov/ct2/show/results/NCT04323592
    if(citekey.startswith ('doi:') and ('(' in citekey or ')' in citekey)):
        short_doi_url = get_short_doi_url(citekey)
        # URL in the form https://doi.org/ggvw2s
        citekey = short_doi_url.replace('https://doi.org', 'doi:10')
    return citekey


def check_none(value):
    """Raises ValueError if value is type None, else returns value"""
    if isinstance(value, type(None)):
        raise ValueError
    return value


def find_country(country):
    """ .get retrieves data as class Country
    .search_fuzzy matching returns a list
    try a few ways to identify a match and
    return as soon as find something valid
    Input is country name (string)
    If no match found, return None"""
    try:
        hit = pycountry.countries.get(name=country)
        hit = check_none(hit)
        return hit
    except (LookupError, ValueError):
        try:
            hit = pycountry.countries.get(official_name=country)
            hit = check_none(hit)
            return hit
        except (LookupError, ValueError):
            try:
                hit = pycountry.countries.search_fuzzy(country)
                hit = check_none(hit)
                if type(hit) == list and len(hit) == 1:
                    return hit[0]
                raise ValueError
            except (LookupError, ValueError):
                try:
                    hit = pycountry.countries.search_fuzzy(country + ",")
                    hit = check_none(hit)
                    if isinstance(hit, list) and len(hit) == 1:
                        return hit[0]
                    else:
                        raise ValueError
                except (LookupError, ValueError):
                    return None


def assign_ISO(countries):
    """ Match country names with ISO codes
    Input: series of country names
    Returns: dictionary of matches
    :type countries: pd.Series """
    # Need to hard code a few countries that aren't registered using standard names, so
    # initializing the country_codes database with these irregular values
    country_codes = {"South Korea": "KOR", "Democratic Republic of Congo": "COD",
                     "Democratic Republic of the Congo": "COD", "UAE": "ARE"}

    # Identify the most likely 3-letter ISO code for each country
    failed_matches = list()
    for country in countries:
        if country not in country_codes.keys():
            # Need to query the pycountry package but it can fail for a
            # few reasons. Use function to avoid LookupError issues and
            # try all the different ways that might help to match a
            # country name to its ISO code
            hit = find_country(country)
            if not isinstance(hit, type(None)):
                country_codes[country] = hit.alpha_3
            else:
                failed_matches.append(country)
    # Print warning about failures and return successes as dictionary
    print("Could not assign country codes to: ", ", ".join(failed_matches))
    return country_codes


def lowres_fix(world):
    """There is an issue with the map data source from geopandas where
    ISO codes are missing for several countries. This fix was proposed
    by @tommycarstensen at
    https://github.com/geopandas/geopandas/issues/1041

    :param world: dataframe (read in with geopandas)
    :return: dataframe (geopandas formatted)
    """
    world.loc[world['name'] == 'France', 'iso_a3'] = 'FRA'
    world.loc[world['name'] == 'Norway', 'iso_a3'] = 'NOR'
    world.loc[world['name'] == 'Somaliland', 'iso_a3'] = 'SOM'
    world.loc[world['name'] == 'Kosovo', 'iso_a3'] = 'RKS'
    return world

def tabulate_countries(trials_df):
    # Clean and separate the names of each country in single-country and
    # multi-country clinical trials. Single-country trials have only a single
    # name (string) in the `countries` field. Multi-country trials have
    # multiple comma-separated names.
    # Drop 1 trial that lists every country.
    valid_country = trials_df[trials_df['countries'] != "No Country Given"]
    valid_country = valid_country[valid_country['trial_id'] != "ISRCTN80453162"]
    single_countries = valid_country['countries'][~valid_country['countries'].str.contains(',')]
    multi_countries = valid_country["countries"][valid_country["countries"].str.contains(',')]
    multi_countries = pd.Series(
        [country for country_list in multi_countries.str.split(',') for country in country_list]
    )

    # Identify the 3-letter ISO codes for each unique country
    # Remove any leading/trailing whitespace that may result from splitting above
    unique_countries = single_countries.append(multi_countries).str.strip().drop_duplicates()
    country_codes = pd.DataFrame.from_dict(assign_ISO(unique_countries),
                                           orient="index",
                                           columns=["iso_a3"])

    # Map the ISO codes onto the country data and count the frequency
    single_countries_codes = pd.DataFrame(single_countries,
                                          index=single_countries).join(country_codes)["iso_a3"]
    single_countries_codes = single_countries_codes.dropna()
    single_countries_counts = single_countries_codes.value_counts()
    multi_countries_codes = \
        pd.DataFrame(multi_countries.str.strip(),
                     index=multi_countries.str.strip()).join(country_codes)["iso_a3"]
    multi_countries_codes = multi_countries_codes.dropna()
    multi_countries_counts = multi_countries_codes.value_counts()
    all_counts = single_countries_counts.to_frame(name='single_countries_counts').\
        merge(multi_countries_counts.to_frame(name='multi_countries_counts'),
              how="outer",
              left_index=True,
              right_index=True)
    return all_counts


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
              'phase', 'study_type', 'countries', 'title', 'acronym', 'study_category', \
              'intervention', 'intervention_list', 'enrollment', \
              'primary_completion_date', 'full_completion_date', 'registy_url', \
              'results_type', 'results_published_date', 'results_url', 'last_updated', \
              'cross_registration']
    assert (len(header) == len(trials_df.columns))
    trials_df.columns = header
    trials_df = trials_df.set_index('index')

    # Filter out trials that are not interventional
    interventional_trials = trials_df[trials_df["study_type"] == "Interventional"]

    ebm_stats['ebm_all_trials'] = f'{len(trials_df.index):,}'
    ebm_stats['ebm_interv_trials'] = f'{len(interventional_trials.index):,}'

    # Get the most recent trial update
    most_recent_update = pd.to_datetime(trials_df['last_updated']).max()
    # Remove the leading zero of the day
    # Assumes the year will not begin with 0
    most_recent_update = most_recent_update.strftime('%B %d, %Y').replace(' 0', ' ')
    ebm_stats['ebm_date_pretty'] = most_recent_update

    trial_results = interventional_trials[interventional_trials['results_url'] != 'No Results']['results_url']
    ebm_stats['ebm_trials_results'] = f'{len(trial_results):,}'

    # Some results entries have multiple URLs
    trial_results_citekeys = [extract_citekey(results_url) for results in trial_results for results_url in results.split()]
    ebm_stats['ebm_trials_results_citekeys'] = sorted(set(trial_results_citekeys))

    plt.rc('font', size=14)
    plt.rc('figure', titlesize=24)
    sns.set_style("ticks")
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20), constrained_layout=True)

    # Plot study type
    # Only include study types used in >= 5 trials
    study_type_counts = trials_df['study_type'].value_counts(ascending=True)
    study_type_counts = study_type_counts[study_type_counts >= 5]
    ax = study_type_counts.plot(kind='barh', ax=axes[0, 0])
    ax.set_title('A. Clinical Trials, Study Type')

    # Plot trial recruitment status
    # Only include interventional trials with a recruitment status
    recruitment_counts = interventional_trials['recruitment_status'].value_counts(ascending=True)
    recruitment_counts = recruitment_counts.drop(labels='No Status Given')
    ax = recruitment_counts.plot(kind='barh', ax=axes[0, 1])
    ax.set_title('B. Clinical Trials, Recruitment Status')

    # Plot trial phase
    # Only include interventional trials with a reported phase
    phase_counts = interventional_trials['phase'].value_counts(ascending=True)
    phase_counts = phase_counts.drop(labels='Not Applicable')
    ax = phase_counts.plot(kind='barh', ax=axes[1, 0])
    ax.set_title('C. Clinical Trials, Phase')

    # Plot common interventions
    # Only include interventional trials with an intervention and interventions in >= 10 trials
    intervention_counts = interventional_trials['intervention'].value_counts(ascending=True)
    intervention_counts = intervention_counts.drop(labels='No Intervention')
    intervention_counts = intervention_counts.drop(labels='Other')
    intervention_counts = intervention_counts[intervention_counts >= 10]
    ax = intervention_counts.plot(kind='barh', ax=axes[1, 1])
    ax.set_title('D. Clinical Trials, Common Interventions')

    fig.savefig(args.output_figure + '.png', dpi=300, bbox_inches = "tight")
    fig.savefig(args.output_figure + '.svg', bbox_inches = "tight")

    print(f'Wrote {args.output_figure}.png and {args.output_figure}.svg')

    # Count geographic representation by ISO3 code
    all_counts = tabulate_countries(interventional_trials)

    # Map frequency data onto the geopandas geographical data for units with ISO code
    # geopandas uses -99 as N/A for this field
    # We don't need to evaluate Antarctica
    countries_mapping = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    countries_mapping = lowres_fix(countries_mapping)
    countries_mapping = countries_mapping[(countries_mapping.name != "Antarctica") &
                                          (countries_mapping.iso_a3 != "-99")]
    countries_mapping = countries_mapping.merge(all_counts,
                                                how="left",
                                                right_index=True,
                                                left_on="iso_a3")

    # Generate two-part choropleth of world map with # of clinical trials counted
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(20, 16))
    fig.patch.set_visible(False)
    ax1.axis('off')
    ax2.axis('off')
    countries_mapping.boundary.plot(ax=ax1, edgecolor="black")
    countries_mapping.plot(column='single_countries_counts', ax=ax1, legend=True)
    ax1.set_title("Number of Single-Country Clinical Trials Recruiting by Country")
    countries_mapping.boundary.plot(ax=ax2, edgecolor="black")
    countries_mapping.plot(column='multi_countries_counts', ax=ax2, legend=True, cmap="Purples")
    ax2.set_title("Number of Multi-Country Clinical Trials Recruiting by Country")
    ax2.annotate(f'Source: EBM Data Lab COVID-19 TrialsTracker, %s' %
                 date.today().strftime("%b-%d-%Y"),
                 xy=(0, 0), xycoords="axes points")

    plt.savefig(args.output_map + '.png', dpi=300, bbox_inches="tight")
    plt.savefig(args.output_map + '.svg', bbox_inches="tight")

    print(f'Wrote {args.output_map}.png and {args.output_map}.svg')

    # The placeholder will be replaced by the actual SHA-1 hash in separate
    # script after the updated image is committed
    ebm_stats['ebm_trials_figure'] = \
        f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.output_figure}.png'
    ebm_stats['ebm_map_figure'] = \
        f'https://github.com/greenelab/covid19-review/raw/$FIGURE_COMMIT_SHA/{args.output_map}.png'
    # Tabulate number of trials for pharmaceuticals of interest
    ebm_stats['ebm_tocilizumab_ct'] = \
        str(interventional_trials['intervention'].str.contains('tocilizumab', case=False).sum())

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
    parser.add_argument('output_map',
                        help='Path of the output choropleth (world map figure) ' \
                        'with geographic clinical trial frequencies, without file ' \
                        'type extension. Will be saved as .png and .svg.',
                        type=str)

    args = parser.parse_args()
    main(args)
