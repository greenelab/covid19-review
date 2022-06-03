import json

def load_JSON(filename):
    with open(filename, 'r') as in_file:
        data = json.load(in_file)
    return data

def write_JSON(data, filename):
    with open(filename, 'w') as out_file:
        json.dump(data, out_file, indent=2, sort_keys=True)
    print(f'Wrote {filename}')
