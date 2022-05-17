#!/bin/bash

# Specify the relative path to the file in the repo
OWID_REPO_PATH=public%2Fdata%2Fvaccinations%2Fvaccinations.json

# Get the most recent commit affecting this file and store the commit sha and date
# See https://stackoverflow.com/questions/50194241/get-when-the-file-was-last-updated-from-a-github-repository/50204589
OWID_COMMIT_JSON=$(curl -sS "https://api.github.com/repos/owid/covid-19-data/commits?path=$OWID_REPO_PATH&per_page=1")
export OWID_COMMIT_SHA=$(echo $OWID_COMMIT_JSON | python -c "import sys, json; print(json.load(sys.stdin)[0]['sha'])")
export OWID_COMMIT_DATE=$(echo $OWID_COMMIT_JSON | python -c "import sys, json; print(json.load(sys.stdin)[0]['commit']['author']['date'])")

# Location of JSON with stats
OWID_STATS_JSON=owiddata/owiddata-stats.json

# The temporary output filenames
VACCINE_PLATFORMS=owiddata/vaccine_platforms.csv
COUNTRY_BY_VAX=owiddata/country_by_vax.json
VAX_BY_MANF=owiddata/vaccination_by_manufacturer.csv

# Locations for images
OWID_MAP=owiddata/maps

echo "Generating Our World in Data COVID-19 vaccine statistics"
#python owiddata/01.OWID.basicStats.py $OWID_STATS_JSON $COUNTRY_BY_VAX $VAX_BY_MANF
#python owiddata/02.VIPER.basicStats.py $OWID_STATS_JSON  $VACCINE_PLATFORMS
#python owiddata/03.integrateDataSources.py $VACCINE_PLATFORMS $COUNTRY_BY_VAX
#python owiddata/04.drawMaps.py $OWID_STATS_JSON $VACCINE_PLATFORMS $OWID_MAP
python owiddata/05.plotadministration.py $OWID_STATS_JSON  $VACCINE_PLATFORMS $VAX_BY_MANF

# Clean up
#rm $VACCINE_PLATFORMS $COUNTRY_BY_VAX

# After running this Python script to generate the figures, commit the figures
# and run the version-figures.sh script to update the OWID_STATS_JSON with the
# versioned figure URL
