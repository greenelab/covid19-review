# Derived from https://github.com/greenelab/deep-review/blob/75f2dd8c61099a17235a4b8de0567b2364901e4d/build/randomize-authors.py
# by Daniel Himmelstein under the CC0 1.0 license
# https://github.com/greenelab/deep-review#license

import argparse
import pathlib
import sys
import yaml
from manubot.util import read_serialized_data

MISSING_AFFILIATIONS = [{"institution": " "}]
MISSING_COI = "None"
ACM_BCB_2021 = {"acm": [{"copyrightyear": "2021",
                         "copyright": "acmcopyright",
                         "conference": "ACM-BCB '21",
                         "conferencetitle": "ACM-BCB '21: ACM Conference on Bioinformatics, Computational Biology, and Health Informatics",
                         "date": "August 01--04, 2021",
                         "location": "Online"}]}


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
        "--manubot_metadata", default="content/metadata.yaml", help="input path to metadata.yaml for Manubot"
    )
    parser.add_argument(
        "--pandoc_metadata", default="content/metadata.yaml", help="output path to metadata.yaml for Pandoc"
    )

    return parser.parse_args()


def dump_yaml(obj, path):
    path = pathlib.Path(path)
    sys.stderr.write(f"Dumping YAML to {path}\n")
    # Needed to address https://stackoverflow.com/questions/13518819/avoid-references-in-pyyaml
    yaml.Dumper.ignore_aliases = lambda *arguments: True
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


def update_latex(keyword, manubot_file, pandoc_file):
    """
    Update Manubot author metadata for an individual manuscript in preparation for LaTeX conversion.
    Prepares a metadata file to override and supplement the metadata in the YAML block in the Markdown
    file Pandoc processes.
    """
    metadata = read_serialized_data(manubot_file)
    authors = metadata.get("authors", [])

    individual_authors = [author for author in authors if "manuscripts" in author and keyword in author["manuscripts"]]
    # Sort authors by their numeric order for this individual manuscript
    # If the author has the manuscript keyword, which indicates authorship, but not an order
    # the default order is -1, which should move them to the front of the author list
    # Sort by name to break ties
    individual_authors.sort(key=lambda author: (author["manuscripts"][keyword].get("order", -1), author["name"]))

    # Set affiliation fields to the manuscript-specific affiliation formatting expected by the LaTeX template
    # and discard fields that will not be used by the LaTeX template
    keep_fields = {"name", "email", "orcid"}  # do not keep the old affiliations
    latex_authors = []
    conflicts = []
    funding = []
    for author in individual_authors:
        latex_author = {field: author[field] for field in keep_fields if field in author}

        # A list of the author's affiliations formatted for the template
        # The first affiliation is stored in the "affiliations" field
        # Any additional affiliations are stored in the "additionalaffiliations" field
        affiliations = author["manuscripts"][keyword].get("affiliations", MISSING_AFFILIATIONS)
        if affiliations == MISSING_AFFILIATIONS:
            sys.stderr.write(f"Missing {keyword} affiliations for {author['name']}\n")

        if len(affiliations) > 0:
            latex_author["affiliations"] = affiliations[0]
        if len(affiliations) > 1:
            latex_author["additionalaffiliations"] = affiliations[1:]
        latex_authors.append(latex_author)

        # Check whether the author has declared conflicts of interest
        if "coi" in author:
            conflict = author["coi"].get("string", MISSING_COI)
            if conflict != "None":
                conflicts.append(f"{author['name']}: {conflict}.")

        # Check whether the author has funding
        # This text will not be used directly but will help write a funding statement manually
        if "funders" in author:
            # Less robust handling of funders field than Manubot
            # https://github.com/manubot/manubot/blob/3ff3000f76dcf82a30694d076a4da95326e3f6ae/manubot/process/util.py#L78
            funders = author["funders"]
            if isinstance(funders, list):
                funders = "; ".join(funders)
            # Assumes initials are always provided
            funding.append(f"{author['initials']}: {funders}.")

    sys.stderr.write(f"Found {len(latex_authors)} authors for {keyword} manuscript\n")

    # Do not retain the other metadata fields and add the .bib file references
    metadata = {"author": latex_authors, "bibfile": keyword + ".bib"}
    metadata.update(ACM_BCB_2021)
    # Add conflicts if any exist
    if len(conflicts) > 0:
        metadata["conflicts"] = "Conflicts of interest. " + " ".join(conflicts)
    # Add funding comment if funders were listed
    if len(funding) > 0:
        metadata["funding"] = "Author funding. " + " ".join(funding)

    dump_yaml(metadata, pandoc_file)


if __name__ == "__main__":
    args = parse_args()
    update_latex(args.keyword, args.manubot_metadata, args.pandoc_metadata)
