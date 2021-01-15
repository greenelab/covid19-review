# Derived from https://github.com/greenelab/deep-review/blob/75f2dd8c61099a17235a4b8de0567b2364901e4d/build/randomize-authors.py
# by Daniel Himmelstein under the CC0 1.0 license
# https://github.com/greenelab/deep-review#license

import argparse
import pathlib
import sys

import yaml
from manubot.util import read_serialized_data


def parse_args():
    parser = argparse.ArgumentParser(
        description="Select authors for an individual manuscript from metadata.authors. "
        "Overwrites metadata.yaml."
    )
    parser.add_argument(
        "--keyword", required=True, help="keyword indicating the individual manuscript (e.g. pathogenesis)"
    )
    parser.add_argument(
        "--path", default="content/metadata.yaml", help="path to metadata.yaml"
    )
    args = parser.parse_args()
    return args

def dump_yaml(obj, path):
    path = pathlib.Path(path)
    sys.stderr.write(f"Dumping YAML to {path}\n")
    with path.open("w", encoding="utf-8") as write_file:
        yaml.dump(
            obj,
            write_file,
            # default_flow_style=False,
            explicit_start=True,
            explicit_end=True,
            width=float("inf"),
            sort_keys=False,
            allow_unicode=True,
        )
        write_file.write("\n")

if __name__ == "__main__":
    """
    Select authors for an individual manuscript. Expects the manuscript keyword
    to be in a list called manuscripts for each author.
    """
    args = parse_args()
    keyword = args.keyword
    
    metadata = read_serialized_data(args.path)
    authors = metadata.get("authors", [])
    individual_authors = [author for author in authors if "manuscripts" in author and keyword in author["manuscripts"]]
    # Sort authors by their numeric order for this individual manuscript
    # If the author has the manuscript keyword, which indicates authorship, but not an order
    # the default order is -1, which should move them to the front of the author list
    # Sort by name to break ties
    individual_authors.sort(key=lambda author: (author["manuscripts"][keyword].get("order", -1), author["name"]))

    sys.stderr.write(f"Found {len(individual_authors)} authors for {keyword} manuscript\n")
    metadata["authors"] = individual_authors
    dump_yaml(metadata, args.path)
