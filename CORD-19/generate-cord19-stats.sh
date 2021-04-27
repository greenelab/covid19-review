#!/bin/bash
# Download EBM Data Lab COVID-19 TrialsTracker data and generate an output JSON file with relevant statistics
# and a figure

# Specify the relative path to the file in the repo
# EBM_REPO_PATH=notebooks%2Fwebsite_data%2Ftrials_latest.json

# Then get the most recent commit affecting this file and store the commit sha and date
# See https://stackoverflow.com/questions/50194241/get-when-the-file-was-last-updated-from-a-github-repository/50204589
# EBM_COMMIT_JSON=$(curl -sS "https://api.github.com/repos/ebmdatalab/covid_trials_tracker-covid/commits?path=$EBM_REPO_PATH&per_page=1")
# export EBM_COMMIT_SHA=$(echo $EBM_COMMIT_JSON | python -c "import sys, json; print(json.load(sys.stdin)[0]['sha'])")
# export EBM_COMMIT_DATE=$(echo $EBM_COMMIT_JSON | python -c "import sys, json; print(json.load(sys.stdin)[0]['commit']['author']['date'])")

CORD19_INPUT_TXT=CORD-19/metadata.readme
CORD19_INPUT_CSV=CORD-19/metadata.csv.zip
CORD19_STATS_JSON=CORD-19/cord19-stats.json
CORD19_FIG=CORD-19/cord19-growth

# I'm not sure how to automate the downloading of a dataset from Kaggle because it requires a key which will be visible?
# echo "Downloading CORD-19 data" # from commit $EBM_COMMIT_SHA authored $EBM_COMMIT_DATE"
# wget https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge/download > kaggle.json
# kaggle datasets download -d allen-institute-for-ai/CORD-19-research-challenge

# After running this Python script to generate the figures, commit the figures
# and run the version-figures.sh script to update the EBM_STATS_JSON with the
# versioned figure URL
# echo "Generating EBM Data Lab COVID-19 TrialsTracker statistics and figure"
# python ebmdatalab/generate-ebmdatalab-stats.py $EBM_INPUT_JSON $EBM_STATS_JSON $EBM_FIG $EBM_MAP
python CORD-19/generate-cord19-stats.py $CORD19_INPUT_TXT $CORD19_INPUT_CSV $CORD19_STATS_JSON $CORD19_FIG
# rm $EBM_INPUT_JSON
