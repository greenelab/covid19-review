#!/usr/bin/env python
# coding: utf-8

# # Generatestats for templated use in the Meta Review
# 
# Note that some statistics are generated from the git submodule, and correspond to the version specified by `commit`. Other statistics are generated from the GitHub API and reflect the repositories status at runtime, as specified by `creation_time_utc`.

# In[19]:


import collections
import datetime
import json
import pathlib
import os

import pandas
import requests
import yaml
import wget


# In[2]:


stats = collections.OrderedDict()
now = datetime.datetime.utcnow()
stats['creation_time_utc'] = now.isoformat()
stats['creation_date_pretty'] = f'{now:%B %d, %Y}'


# ## Git repository stats

# In[3]:


commit_df = pandas.read_csv('commits.tsv', sep='\t')
commit_df.tail(2)


# In[4]:


# State of the git repo (deep-review submodule)
stats['commit'] = commit_df.commit.iloc[-1]


# In[5]:


stats['total_commits'] = len(commit_df)


# In[6]:


# Number of non-merge commits that modified the manuscript markdown source
writing_commit_df = commit_df.query("(characters_added > 0 or characters_deleted > 0) and merge == 0")
stats['manuscript_commits'] = len(writing_commit_df)


# ### Number of formal authors

# In[7]:


metadataURL="https://raw.githubusercontent.com/greenelab/covid19-review/master/content/metadata.yaml"
metadataDownload = wget.download(metadataURL, out="metadata.yaml")
with open("metadata.yaml", "r") as read_file:
    metadata = yaml.load(read_file)
print(metadata)


# In[8]:


authors = metadata['authors']
stats['review_authors'] = len(authors)


# ## GitHub repo stats

# In[9]:


# https://developer.github.com/v3/repos/#get
response = requests.get('https://api.github.com/repos/greenelab/covid19-review')
result = response.json()
stats['github_stars'] = result['stargazers_count']
stats['github_forks'] = result['forks_count']


# ### Number of pull requests

# In[10]:


def github_issue_search(query):
    """
    Search issues and pull requests on GitHub.

    https://developer.github.com/v3/search/#search-issues
    https://help.github.com/articles/searching-issues-and-pull-requests/
    """
    url = 'https://api.github.com/search/issues'
    params = {
        'q': query,
        'sort': 'created',
        'order': 'asc',
    }
    response = requests.get(url, params)
    print(response.url)
    assert response.status_code == 200
    result = response.json()
    assert not result['incomplete_results']
    return result


# In[11]:


# Merged PRs
result = github_issue_search('repo:greenelab/covid19-review type:pr is:merged')
stats['merged_pull_requests'] = result['total_count']


# In[12]:


# Closed PRs that were not merged
result = github_issue_search('repo:greenelab/covid19-review type:pr is:unmerged state:closed')
stats['declined_pull_requests'] = result['total_count']


# In[13]:


# Open PRs
result = github_issue_search('repo:greenelab/covid19-review type:pr state:open')
stats['open_pull_requests'] = result['total_count']


# In[14]:


# Open Issues
result = github_issue_search('repo:greenelab/covid19-review type:issue state:open')
stats['open_issues'] = result['total_count']


# In[15]:


# Closed Issues
result = github_issue_search('repo:greenelab/covid19-review type:issue state:closed')
stats['closed_issues'] = result['total_count']


# ## Write stats

# In[16]:


stats_str = json.dumps(stats, indent=2)
print(stats_str)


# In[17]:


path = pathlib.Path('covid19-review-stats.json')
path.write_text(stats_str)


# In[20]:


os.remove("metadata.yaml") 


# In[ ]:




