#!/bin/bash
# Download EBM Data Lab COVID-19 TrialsTracker data and generate an output JSON file with relevant statistics
# and a figure

# Then get the most recent commit affecting this file and store the commit sha and date
# See https://stackoverflow.com/questions/50194241/get-when-the-file-was-last-updated-from-a-github-repository/50204589
OWID_COMMIT_JSON=$(curl -sS "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.json")
export OWID_COMMIT_SHA=$(echo $OWID_COMMIT_JSON | python -c "import sys, json; print(json.load(sys.stdin)[0]['sha'])")
export OWID_COMMIT_DATE=$(echo $OWID_COMMIT_JSON | python -c "import sys, json; print(json.load(sys.stdin)[0]['commit']['author']['date'])")

OWID_STATS_JSON=owiddata/owiddata-stats.json

# After running this Python script to generate the figures, commit the figures
# and run the version-figures.sh script to update the EBM_STATS_JSON with the
# versioned figure URL
echo "Generating Our World in Data COVID-19 vaccine statistics"
python ebmdatalab/generate-ebmdatalab-stats.py $EBM_STATS_JSON
