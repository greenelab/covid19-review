import pandas as pd
import requests
import json
import base64
import logging
from manubot import cite


headers = {}  # For Development you can insert your GH api token here and up the rate limit {'Authorization': 'token %s' % "<apiToken>"}


# Issues Helper Functions
def getIssuesFromAPI():
    """ Gets all the issues and pull-requests (GH treats PRs like issues in the api)
    Needs to use pagination because of 100 per-request api limit
    """
    issues = []
    pageNumber = 1
    numberOfIssuesReturned = 1
    while numberOfIssuesReturned != 0:
        issuesResponse = requests.get(
            "https://api.github.com/repos/greenelab/covid19-review/issues?state=all&per_page=50&page=" +
            str(pageNumber), headers=headers)
        issues_page = json.loads(issuesResponse.text)
        issues = issues + issues_page
        numberOfIssuesReturned = len(issues_page)
        pageNumber += 1
    return issues


def getCitationFromIssue(issue):
    """ Gets the citation from the github issue assuming the issue follows the New Paper issue template
    Citation is typically a DOI but could be something else
    """
    try:
        if "\nCitation: " in issue["body"]:
            citation = issue["body"].split("\nCitation: ")[1].split(" ")[0]
        else:
            afterDOI = issue["body"].split("DOI:")[1]
            citation = afterDOI.split(" ")[0]
            if citation == "":
                citation = afterDOI.split(" ")[1]
        if "\r\n" in citation:
            citation = citation.split("\r\n")[0]
        if citation.startswith("@"):
            citation = citation[1:]
        return citation

    except:
        print(
            "the citation could not be automatically extracted from the following issue: \n",
            issue["title"])
        return "unknown"


def getPaperTitleFromIssue(issue):
    """ gets the papers title using manubot; if manubot can't get title, extract from issue title """
    try:
        # Try using manubot
        citekey = getCitationFromIssue(issue)
        csl_item = cite.citekey_to_csl_item(citekey)
        title = csl_item["title"]
        return title
    except:
        # On error, try getting from issue title
        try:
            title = issue["title"].split(":")[1]
            return title
        except:
            print(
                "the paper title could not be automatically extracted from the following issue: \n",
                issue["title"])
            return "unknown"


def citationContainsDOI(citation):
    """ Checks if the citation contains a doi """
    if citation.startswith("doi:"):
        return True
    elif citation.startswith("@doi:"):
        return True
    elif citation.startswith("[@doi"):
        return True
    else:
        return False


def getDOIFromCitation(citation):
    """ pulls the DOI from the citation; built to handle the cases I've seen so far """
    try:
        if ".org/" in citation:
            DOI = citation.split(".org/")[1]
        elif citationContainsDOI(citation):
            DOI = citation.split("doi:")[1]
        elif citation == "unknown":
            DOI = "unknown"
        else:
            DOI = citation
        # DOIs are case insensitive but lower-case seems to be preferred and is what's used by manubot
        DOI = DOI.lower()
        return DOI
    except:
        return "unknown"


def getIssuesDF(issues, removeDuplicates=True):
    """ takes a list of github issues
    Assumes they are all New Paper issues
    Creates a data frame with doi, title, issueLink and issueLabels
    issue labels is a comma seperated string
    """
    DOIs = []
    titles = []
    issue_links = []
    lables = []
    for issue in issues:
        DOIs.append(getDOIFromCitation(getCitationFromIssue(issue)))
        titles.append(getPaperTitleFromIssue(issue))
        issue_links.append(issue["html_url"])
        lables.append(", ".join([label["name"] for label in issue["labels"]]))
    issuesDF = pd.DataFrame({
        "doi": DOIs,
        "title": titles,
        "gh_issue_link": issue_links,
        "gh_issue_labels": lables}).set_index("doi")
    if removeDuplicates:
        issuesDF = issuesDF[~issuesDF.gh_issue_labels.str.contains("duplicate")]
    return issuesDF


def getIssuesData():
    issues = getIssuesFromAPI()
    paperIssues = [issue for issue in issues if "New Paper (" in issue["title"]]
    paperIssuesDF = getIssuesDF(paperIssues)

    # log the issues without valid DOIs
    doesNotHaveValidDOI = [not doi.startswith("10") for doi in list(paperIssuesDF.index)]
    issueLinksWithoutDOIs = list(paperIssuesDF.gh_issue_link[doesNotHaveValidDOI])
    print('\n\nA valid DOIs could not be extracted from the following', len(issueLinksWithoutDOIs), 'issues:\n', issueLinksWithoutDOIs, '\n')

    return paperIssuesDF


# Covid19-review citations functions
def getCitationsData():
    """ Gets a dataframe with doi, title, date, publication, url and covid19-review_paperLink
    The covid19-review_paperLink is a link to that paper's citation in the html document (example: https://greenelab.github.io/covid19-review/#ref-Rt5Aik4p)
    Gets the citation info from the referneces.json file in the output branch
    """
    citationsResponse = requests.get("https://api.github.com/repos/greenelab/covid19-review/contents/references.json?ref=output", headers=headers)
    citations = json.loads(base64.b64decode(json.loads(citationsResponse.text)["content"]))
    citationsDF = pd.DataFrame(citations)
    citationsDF["Covid19-review_paperLink"] = citationsDF.id.apply(lambda x: "https://greenelab.github.io/covid19-review/#ref-" + x)
    citationsDF = citationsDF[["DOI", "title", "issued", "container-title", "URL", "Covid19-review_paperLink"]]
    citationsDF.rename(columns={"DOI": "doi", "issued": "date", "container-title": "publication"}, inplace=True)

    # Convert date to string
    def dateStringFromDateParts(row):
        try:
            dateParts = row['date']['date-parts'][0]
            if len(dateParts) == 3:
                return "-".join([str(dateParts[1]), str(dateParts[2]), str(dateParts[0])])
            elif len(dateParts) == 2:
                return "-".join([str(dateParts[1]), str(dateParts[0])])
            elif len(dateParts) == 1:
                return str(dateParts[0])
            else:
                return
        except:
            return

    citationsDF.date = citationsDF.apply(dateStringFromDateParts, axis=1)

    citationsDF.set_index("doi", inplace=True)
    return citationsDF


def mergePaperDataFrames(dataFramesList):
    """ Combine a list of paper dataframes into one.

    Each data frame should have the doi as index.
    Can have title and date columns; the tile and date from the first dataframe in the list will be kept in case of conflict.
    Any additional columns unique to dataset will be kept.
    """
    print(sum([len(df) for df in dataFramesList]), "total items to merge")

    # Add "_#" to title and date columns of all but the first df
    for i in range(len(dataFramesList)):
        if i == 0: continue
        dataFramesList[i] = dataFramesList[i].rename(columns={"title": ("title_" + str(i)), "date": ("date_" + str(i))})

    # Seperate into items with and without valid DOIs
    dataFramesList_DOI = []
    dataFramesList_NoDOI = []
    for df in dataFramesList:
        validDOI = [str(index).startswith("10") for index in df.index]
        invalidDOI = [False if val else True for val in validDOI]
        dataFramesList_DOI.append(df[validDOI])
        dataFramesList_NoDOI.append(df[invalidDOI])

    # Merge on DOIs
    mergedOnDOI = pd.concat(dataFramesList_DOI, axis=1, sort=False)
    mergedOnDOI['doi'] = mergedOnDOI.index

    # TODO: merge on titles

    # Add in the items that didn't have a DOI
    dfsToMerge = dataFramesList_NoDOI
    dfsToMerge.append(mergedOnDOI)
    merged = pd.concat(dfsToMerge, axis=0, ignore_index=True, sort=False)

    # Combine the title and date info from duplicate columns
    for i in range(len(dataFramesList)):
        if i == 0: continue
        for col in ['title', 'date']:
            secondaryCol = col + "_" + str(i)
            if secondaryCol in merged.columns:
                merged[col] = merged[col].combine_first(df[secondaryCol])
                merged.drop(secondaryCol, axis=1, inplace=True)

    return merged


# Main
# log only critical manubot errors
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)
print("\n -- getting issues data --")
issuesData = getIssuesData()
print(len(issuesData), "'New Paper' issues")
print("\n -- getting citations data --")
citationsData = getCitationsData()
print(len(citationsData), "citations in the covid19-review paper")
# TODO: pullRequestsData = getPullRequestData()

print("\n -- merging the data --")
combinedData = mergePaperDataFrames([citationsData, issuesData])
print(len(combinedData), "total items after merge")


combinedDataFilePath = "./output/sources_cross_reference.tsv"
print("\n -- saving the data to ", combinedDataFilePath, " --")
combinedData.to_csv(combinedDataFilePath, sep="\t")
