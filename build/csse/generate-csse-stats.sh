#!/bin/bash
# Download JHU CSSE data and generate an output JSON file with relevant statistics
# and a figure
export CSSE_COMMIT=$(curl -sS https://api.github.com/repos/CSSEGISandData/COVID-19/branches/master | python -c "import sys, json; print(json.load(sys.stdin)['commit']['sha'])")
CSSE_CSV=output/csse/time_series_covid19_deaths_global.csv
export CSSE_JSON=output/csse/csse-stats.json

mkdir -p output/csse
echo "Downloading JHU CSSE data from commit $CSSE_COMMIT"
curl -fsSL https://github.com/CSSEGISandData/COVID-19/raw/$CSSE_COMMIT/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv > $CSSE_CSV

echo "Generating JHU CSSE statistics and figure"
python build/csse/generate-csse-stats.py $CSSE_CSV $CSSE_JSON
