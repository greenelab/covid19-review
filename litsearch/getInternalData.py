import pandas as pd
import requests
import json
import base64


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
            str(pageNumber))
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
        return citation

    except:
        print(
            "the citation could not be automatically extracted from the following issue: \n",
            issue["title"])
        return "unknown"


def getPaperTitleFromIssue(issue):
    """ gets the papers title from the issue title """
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
        return DOI
    except:
        return "unknown"


def getIssuesDF(issues):
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
    return issuesDF


def getIssuesData():
    issues = getIssuesFromAPI()
    paperIssues = [issue for issue in issues if "New Paper (" in issue["title"]]
    paperIssuesDF = getIssuesDF(paperIssues)
    return paperIssuesDF


# Covid19-review citations functions
def getCitationsData():
    """ Gets a dataframe with doi, title, date, publication, url and covid19-review_paperLink
    The covid19-review_paperLink is a link to that paper's citation in the html document (example: https://greenelab.github.io/covid19-review/#ref-Rt5Aik4p)
    Gets the citation info from the referneces.json file in the output branch
    """
    citationsResponse = requests.get("https://api.github.com/repos/greenelab/covid19-review/contents/references.json?ref=output")
    citations = json.loads(base64.b64decode(json.loads(citationsResponse.text)["content"]))
    citationsDF = pd.DataFrame(citations)
    citationsDF["Covid19-review_paperLink"] = citationsDF.id.apply(lambda x: "https://greenelab.github.io/covid19-review/#ref-" + x)
    for col in citationsDF.columns:
        print(col)
    citationsDFforTSV = citationsDF[["DOI", "title", "issued", "container-title", "URL", "Covid19-review_paperLink"]]
    citationsDFforTSV.rename(columns={"DOI": "doi", "issued": "date", "container-title": "publication"}, inplace=True)
    citationsDFforTSV.set_index("doi", inplace=True)
    return citationsDFforTSV


def mergePaperDataFrames(dataFramesList):
    # TODO: Merge the data sets, try with DOI then fuzzy match titles
    
    # just returning the first one as a placeholder
    return dataFramesList[0]


# Main
print("\n -- getting issues data --")
issuesData = getIssuesData()
print(len(issuesData), "'New Paper' issues")
print("\n -- getting citations data --")
citationsData = getCitationsData()
print(len(citationsData), "citations in the covid19-review paper")
# TODO: pullRequestsData = getPullRequestData()

print("\n -- merging the data --")
combinedData = mergePaperDataFrames([issuesData, citationsData])
print(len(combinedData), "total papers")

# TODO: decide how and where to save the resulting TSV (output branch? main branch? via CI? via github actions?)
combinedDataFilePath = "./covid19-reviewPaperMetaData.tsv"
print("\n -- saving the data to ", combinedDataFilePath, " --")
combinedData.to_csv(combinedDataFilePath, sep="\t")
