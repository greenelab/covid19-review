import requests
import lxml.html as lh
import sys

# This code is adapted from https://towardsdatascience.com/web-scraping-html-tables-with-python-c9baba21059

url="https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html"

# Parse the table only
releaseInfo = requests.get(url)
pageText = lh.fromstring(releaseInfo.content)
tableContents = pageText.xpath('//tr')

extractedTable=dict()
# We are interested in the first two rows. The first gives us the header
for col in range(0, len(tableContents[0])):
    name = tableContents[0][col].text_content()
    content = tableContents[1][col].text_content()
    extractedTable[name]=content

print(extractedTable["Date"] + "." + extractedTable["sha1"], file=sys.stdout)
