import sys
import json

with open(sys.argv[1], 'r') as infile:
    data = json.load(infile)
    if 'commit' in data:
        print(data['commit']['sha'])
    else:
        sys.exit(f'Unexpected response from external-resources branch:\n {data}')