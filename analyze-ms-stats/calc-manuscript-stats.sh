# Calculate growth statistics for manuscript based on Manubot files

# Generate list of all commits in history of output branch
git log --pretty=format:"%h" --first-parent output > output-commits.txt

# Define input and output files
COMMIT_LIST=./output-commits.txt
OUTPUT_JSON=manuscript_stats.json
OUTPUT_FIG=manuscript_stats

# Run python script
python calc-manuscript-stats.py $COMMIT_LIST $OUTPUT_JSON $OUTPUT_FIG

# Clean up temporary files
rm ./references_tmp.json ./variables_tmp.json output-commits.txt
