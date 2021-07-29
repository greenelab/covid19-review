#!/bin/bash
# Download JHU CSSE data
export CSSE_COMMIT=$(curl -sS https://api.github.com/repos/CSSEGISandData/COVID-19/branches/master | python -c "import sys, json; print(json.load(sys.stdin)['commit']['sha'])")
# Don't need for SARS data because it is not likely to be udpated

# Generate an output JSON file with relevant statistics and figure
CSSE_DEATHS_CSV=csse/time_series_covid19_deaths_global.csv
CSSE_CASES_CSV=csse/time_series_covid19_cases_global.csv
SARS_CSV=csse/time_series_sars.csv
CSSE_STATS_JSON=csse/csse-stats.json
CSSE_FIG=csse/csse-deaths

echo "Downloading JHU CSSE data from commit $CSSE_COMMIT"
curl -fsSL https://github.com/CSSEGISandData/COVID-19/raw/$CSSE_COMMIT/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv > $CSSE_DEATHS_CSV
curl -fsSL https://github.com/CSSEGISandData/COVID-19/raw/$CSSE_COMMIT/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv > $CSSE_CASES_CSV

echo "Downloading SARS data scraped from WHO (on GitHub)"
curl -fsSL https://raw.githubusercontent.com/imdevskp/sars-2003-outbreak-data-webscraping-code/master/sars_2003_complete_dataset_clean.csv > $SARS_CSV

# After running this Python script to generate the figures, commit the figures
# and run the version-figures.sh script to update the CSSE_STATS_JSON with the
# versioned figure URL
echo "Generating JHU CSSE statistics and figure"
python csse/generate-csse-stats.py $CSSE_DEATHS_CSV $CSSE_CASES_CSV $SARS_CSV $CSSE_STATS_JSON $CSSE_FIG

rm $CSSE_DEATHS_CSV $CSSE_CASES_CSV $SARS_CSV
