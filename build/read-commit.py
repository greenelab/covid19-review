import sys
import json
import os

with open('commitinfo.json', 'r') as infile:
    data = json.load(infile)
    if 'commit' in data:
        print(data['commit']['sha'])
    else:
        print(data)
        exit(1)