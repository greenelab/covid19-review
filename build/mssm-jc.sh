#!/bin/bash

# Get the SHA-1 hash of the latest commit on the master branch
# See https://developer.github.com/v3/repos/branches/
# and https://stackoverflow.com/questions/1955505/parsing-json-with-unix-tools
ISMMS_COMMIT=05d387bf10b829dad6bedb4bf313686750b78cc9

echo "Downloading content from commit $ISMMS_COMMIT"
curl -fsSL https://github.com/ismms-himc/covid-19_sinai_reviews/archive/$ISMMS_COMMIT.zip > output/MSSM.zip

echo "Unzipping output/MSSM.zip"
unzip -q output/MSSM.zip covid-19_sinai_reviews-$ISMMS_COMMIT/markdown_files/*

echo "Writing appendix file"
# Add a header comment with the SHA-1 of the reviews repository
echo -e "<!-- Appendix source: https://github.com/ismms-himc/covid-19_sinai_reviews/tree/$ISMMS_COMMIT -->\n" > content/95-ismms-himc-appendix.md

# This is not at all elegant, but without two trailing newlines the headers don't work. I had this without temp files but couldn't get the newlines working.
for x in covid-19_sinai_reviews-$ISMMS_COMMIT/markdown_files/*; do cat $x > tmp.`basename $x`; echo -e "\n" >> tmp.`basename $x`; done

cat tmp.* >> content/95-ismms-himc-appendix.md

echo "Cleaning up repository"
rm output/MSSM.zip
rm -r covid-19_sinai_reviews-$ISMMS_COMMIT
rm tmp.*
