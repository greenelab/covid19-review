#!/bin/bash

curl -fSL https://github.com/ismms-himc/covid-19_sinai_reviews/archive/master.zip > MSSM.zip

unzip MSSM.zip covid-19_sinai_reviews-master/markdown_files/*

# This is not at all elegant, but without two trailing newlines the headers don't work. I had this without temp files but couldn't get the newlines working.
for x in covid-19_sinai_reviews-master/markdown_files/*; do cat $x > tmp.`basename $x`; echo -e "\n" >> tmp.`basename $x`; done

cat tmp.* > content/95-ismms-himc-appendix.md
rm MSSM.zip
rm -r covid-19_sinai_reviews-master
rm tmp.*
