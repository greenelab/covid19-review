#!/bin/bash

# After running this Python script to generate the figures, commit the figures
# and run the version-figures.sh script to update the CONTRIB_STATS_JSON with the
# versioned figure URL

echo "Generating contributor statistics and figure"
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=python3 --output output.ipynb contrib-viz/01.contrib-git.ipynb
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=ir --output output.ipynb contrib-viz/02.contrib-viz.ipynb
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=python3 --output output.ipynb contrib-viz/03.contrib-stats.ipynb

# Remove temporary files
rm contrib-viz/commits.tsv contrib-viz/contributors.tsv output.ipynb
