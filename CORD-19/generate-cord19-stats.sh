#!/bin/bash
# Prepare to download the CORD-19 dataset and to generate an output JSON file with relevant statistics
# and a figure using the associated Python script

# Parse the release info to pull the most recent date and SHA (separated by a .)
CORD19_VERSION=$(python CORD-19/parse_html.py)

# Set the filenames/locations of the output files
CORD19_STATS_JSON=CORD-19/cord19-stats.json
CORD19_FIG=CORD-19/cord19-growth

# After running this Python script to generate the figures, commit the figures
# and run the version-figures.sh script to update the CORD-19 figures with the
# versioned figure URL

echo "Generating CORD-19 statistics and figure"
python CORD-19/generate-cord19-stats.py $CORD19_VERSION $CORD19_STATS_JSON $CORD19_FIG

# Clean up downloaded files
rm CORD-19/metadata.csv 2> /dev/null
rm CORD-19/changelog.txt 2> /dev/null
