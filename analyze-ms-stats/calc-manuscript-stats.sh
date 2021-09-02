# Calculate growth statistics for manuscript based on Manubot files

# Generate list of all commits in history of output branch
echo "Generate log for output branch"
git log --pretty=format:"%h" --first-parent output > analyze-ms-stats/output-commits.txt

# Define input and output files
COMMIT_LIST=analyze-ms-stats/output-commits.txt
OUTPUT_JSON=analyze-ms-stats/manuscript_stats.json
OUTPUT_FIG=content/images/manuscript_stats

# Run python script
echo "Run python script"
python analyze-ms-stats/calc-manuscript-stats.py $COMMIT_LIST $OUTPUT_JSON $OUTPUT_FIG

# Clean up temporary files
echo "Clean up temporary files"
rm ./references_tmp.json ./variables_tmp.json analyze-ms-stats/output-commits.txt
