#!/bin/bash

# Specify the relative path to the file in the repo
OWID_REPO_PATH=public%2Fdata%2Fvaccinations%2Fvaccinations.json


# Get the most recent commit affecting this file and store the commit sha and date
# See https://stackoverflow.com/questions/50194241/get-when-the-file-was-last-updated-from-a-github-repository/50204589
OWID_COMMIT_JSON=$(curl -sS "https://api.github.com/repos/owid/covid-19-data/commits?path=$OWID_REPO_PATH&per_page=1")
export OWID_COMMIT_SHA=$(echo $OWID_COMMIT_JSON | python -c "import sys, json; print(json.load(sys.stdin)[0]['sha'])")
export OWID_COMMIT_DATE=$(echo $OWID_COMMIT_JSON | python -c "import sys, json; print(json.load(sys.stdin)[0]['commit']['author']['date'])")

# The output filename
OWID_STATS_JSON=owiddata/owiddata-stats.json

echo "Generating Our World in Data COVID-19 vaccine statistics"
python owiddata/generate-owiddata-stats.py $OWID_STATS_JSON

# After running this Python script to generate the figures, commit the figures
# and run the version-figures.sh script to update the OWID_STATS_JSON with the
# versioned figure URL
