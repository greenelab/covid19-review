# Derived from https://github.com/greenelab/deep-review/blob/75f2dd8c61099a17235a4b8de0567b2364901e4d/build/randomize-authors.py
# by Daniel Himmelstein under the CC0 1.0 license
# https://github.com/greenelab/deep-review#license

import argparse
import pathlib
import sys

import yaml
from manubot.util import read_serialized_data

MISSING_CONTRIBUTIONS = ["**MISSING**"]

def parse_args():
    parser = argparse.ArgumentParser(
        description="Select authors for an individual manuscript from metadata.authors "
        "or update author metadata for the merged manuscript. Overwrites metadata.yaml."
    )
    parser.add_argument(
        "--keyword", required=True, help="keyword indicating the individual manuscript "
        "(e.g. 'pathogenesis') or 'merged' to update author metadata for the merged manuscript"
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

def update_merged(path):
    """
    Update author contributions for the merged manuscript by taking the union
    of all contributions on individual manuscripts
    """
    
def update_individual(path, keyword):
    """
    Select authors for an individual manuscript. Expects the manuscript keyword
    to be in a dictionary called manuscripts for each author of that manuscript.
    """
    metadata = read_serialized_data(path)
    authors = metadata.get("authors", [])
    individual_authors = [author for author in authors if "manuscripts" in author and keyword in author["manuscripts"]]
    # Sort authors by their numeric order for this individual manuscript
    # If the author has the manuscript keyword, which indicates authorship, but not an order
    # the default order is -1, which should move them to the front of the author list
    # Sort by name to break ties
    individual_authors.sort(key=lambda author: (author["manuscripts"][keyword].get("order", -1), author["name"]))

    # Set contributions to the appropriate manuscript-specific contributions
    for author in individual_authors:
        # A list of the author's contributions for this manuscript
        contributions = author["manuscripts"][keyword].get("contributions", MISSING_CONTRIBUTIONS)
        if contributions == MISSING_CONTRIBUTIONS:
            sys.stderr.write(f"Missing {keyword} contributions for {author['name']}\n")
        author["contributions"] = sorted(contributions)

    sys.stderr.write(f"Found {len(individual_authors)} authors for {keyword} manuscript\n")
    metadata["authors"] = individual_authors
    dump_yaml(metadata, path)

if __name__ == "__main__":
    args = parse_args()
    if args.keyword.lower() == "merged":
        update_merged(args.path)
    else:
        update_individual(args.path, args.keyword)
