import spacy
from scispacy.abbreviation import AbbreviationDetector
import numpy as np
import pandas as pd
from os import path
import re

def identify_acronyms(fileName, text, abbrevMeanings):
    """Use spacy to identify abbreviation tokens & match them with their longform meanings
    Accepts: string in which to identify abbreviations, dictionary of known abbrev/meaning pairs
    Returns: dictionary with key: abbreviation, values of Definition (long-form meaning),
             AbbrevCount (how many times abbreviation appears in full text), PhraseCount (how
             many times the long-form meaning appears in the text), Document (the part of the ms
             where the acronym is first used), Position (the position in the document where
             the acronym is first used), as well as a list of the new abbreviations added
    Adapted from a Stack Overflow response by Davide Fiocco
    https://stackoverflow.com/questions/52570805/how-to-identify-abbreviations-acronyms-and-expand-them-in-spacy
    """
    doc = nlp(text)
    newAbbrev = list()
    for abrv in doc._.abbreviations:
        if abrv.text not in abbrevMeanings.keys():
            abbrevMeanings[abrv.text] = {'Definition': str(abrv._.long_form),
                                         'AbbrevCount': 0,
                                         'PhraseCount': 0,
                                         'Document': fileName,
                                         'Position': abrv.start}
            newAbbrev.append(abrv.text)
        elif int(abbrevMeanings[abrv.text]['Document'][0:2]) < int(fileName[0:2]):
            abbrevMeanings[abrv.text]['Document'] = fileName
            abbrevMeanings[abrv.text]['Position'] = abrv.start
        elif abbrevMeanings[abrv.text]['Document'] == fileName and abrv.start < abbrevMeanings[abrv.text]['Position']:
            abbrevMeanings[abrv.text]['Position'] = abrv.start
    return abbrevMeanings, newAbbrev

def count_acronyms(text, abbrevMeanings):
    """Counts how many times the acronym & its long-form appear in the text
    Accepts: string in which to count abbreviations, dictionary of known abbrev/meaning pairs
    Returns: dictionary with key: abbreviation, value: [long-form meaning, number of occurrences]"""
    for abrv in abbrevMeanings.keys():
        if abbrevMeanings[abrv]["Definition"] is np.nan:
            # Erroneously detected acronym must have definition set manually to None
            continue
        abbrevMeanings[abrv]['AbbrevCount'] += len(re.findall(abrv, text))
        phrase = re.compile(re.escape(abbrevMeanings[abrv]['Definition']))
        abbrevMeanings[abrv]['PhraseCount'] += len(re.findall(phrase, text))
    return abbrevMeanings

# Load reference tokens - for mac must be installed as: /usr/local/bin/python3.8 -m spacy download en_core_web_md
nlp = spacy.load('en_core_web_md')

# Set up Abbreviation Detector
abbreviation_pipe = AbbreviationDetector(nlp)
nlp.add_pipe(abbreviation_pipe)

# If abbreviations have already been curated, use the existing list
if path.exists("abbreviations.tsv"):
    abbreviations = pd.read_csv("abbreviations.tsv", sep='\t', index_col="Abbreviation", na_values="None")
    for col in ["AbbrevCount", "PhraseCount"]:
        abbreviations[col] = [0] * len(abbreviations.index)
    abbreviations = abbreviations.to_dict('index')

else:
    # Otherwise, seed dictionary with SARS-CoV-2, which is not detected by scispacy
    abbreviations = {'SARS-CoV-2': {'Definition': "Severe acute respiratory syndrome coronavirus 2",
                                    'AbbrevCount': 0,
                                    'PhraseCount': 0,
                                    'Document': "02.introduction",
                                    'Position': 230}}

# Read in each section of the text and identify abbreviations
fulltext = ""
newAbbrev = list()
for section in ['02.introduction','07.pathogenesis', '08.transmission', '10.diagnostics',
                '20.treatments', '50.discussion', '60.methods']:
    textFile = open('../../content/' + section + '.md', 'r')
    text = textFile.read()

    # Add any new acronyms to the dictionary
    dictUpdates, abbrevUpdates = identify_acronyms(section, text, abbreviations)
    abbreviations.update(dictUpdates)
    newAbbrev += abbrevUpdates
    fulltext += text + '\n'
# Update counts of acronyms across full text
abbreviations.update(count_acronyms(fulltext, abbreviations))

# Save abbreviations and information to file that can be manually curated
abbreviations = pd.DataFrame.from_dict(abbreviations, orient='index', columns = ["Definition",
                                                                                 "AbbrevCount",
                                                                                 "PhraseCount",
                                                                                 "Document",
                                                                                 "Position"])
abbreviations = abbreviations.sort_index()
abbreviations.index.name = "Abbreviation"
abbreviations.to_csv("abbreviations.tsv", sep="\t", na_rep="None")

# Inform user of new acronyms added, if applicable
# Plan to convert to function of AppVeyorBot for future versions
if len(newAbbrev) > 0:
    print("New acronyms added:")
    for abrv in newAbbrev:
        print(abrv)
