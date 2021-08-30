#!/usr/bin/env python
# coding: utf-8

# # Extract GitHub contributions over time
# 
# Uses [GitPython](http://gitpython.readthedocs.io/en/stable/).

# In[1]:


import collections
import pathlib
import re
import datetime
import git
import pandas
import pytz


# In[2]:


repo = git.Repo(path = '../')
repo.head.reference = "master"
print(repo.head.commit)


# In[3]:


# These patterns are reversed because our diffs are backwards
# -R (R=True, suggested in https://git.io/vdigv) doesn't seem to work
added_pattern = re.compile(r'^-(.+)', flags=re.MULTILINE)
deleted_pattern = re.compile(r'^\+(.+)', flags=re.MULTILINE)
pattern_alphanum = re.compile(r'\w')

def get_word_count(text):
    """
    Compute word count of text. Splits by whitespace and only retains
    words with at least one alphanumeric character [a-zA-Z0-9_].
    """
    words = text.split()
    words = list(filter(pattern_alphanum.match, words))
    return len(words)

def get_commit_stats(commit):
    """
    Return addition and deletion (based on `git diff --word-diff`) for a commit.
    
    https://git-scm.com/docs/git-diff
    http://gitpython.readthedocs.io/en/stable/reference.html#module-git.diff
    """
    diffs = commit.diff(
        other=commit.parents[0] if commit.parents else git.NULL_TREE,
        paths=['sections/*.md', 'content/*.md'],
        create_patch=True,
        word_diff='porcelain',
    )

    delta = collections.OrderedDict()
    for key in 'words_added', 'words_deleted', 'characters_added', 'characters_deleted':
        delta[key] = 0
    for diff in diffs:
        diff_str = str(diff)
        additions = added_pattern.findall(diff_str)
        deletions = deleted_pattern.findall(diff_str)

        # Attempt to ignore relocated lines
        additions, deletions = (
            [x for x in additions if get_word_count(x) < 4 or x not in set(deletions)],
            [x for x in deletions if get_word_count(x) < 4 or x not in set(additions)],
        )
        for added in additions:
            delta['words_added'] += get_word_count(added)
            delta['characters_added'] += len(added)
        for deleted in deletions:
            delta['words_deleted'] += get_word_count(deleted)
            delta['characters_deleted'] += len(deleted)
    return(delta)


# In[4]:


rows = list()
# We want to filter out anything from the Manubot development project that predates the COVID-19 project
# The COVID-19 project began on 3/20/2020, but let's build in one extra day just in case timezones cause issues
tz = pytz.timezone('America/New_York')
project_start = datetime.datetime(2020, 3, 19, 0, 0, 0, tzinfo=tz)
for commit in repo.iter_commits():
    if commit.authored_datetime < project_start:
        continue
    row = collections.OrderedDict()
    row['commit'] = commit.hexsha
    row['author_name'] = commit.author.name
    row['author_email'] = commit.author.email
    row['committer_name'] = commit.committer.name
    row['authored_datetime'] = commit.authored_datetime
    row['committed_datetime'] = commit.committed_datetime
    row['summary'] = commit.summary
    row['count'] = commit.count()
    row['merge'] = int(len(commit.parents) > 1)
    row['parents'] = ', '.join(x.hexsha for x in commit.parents)
    row.update(get_commit_stats(commit))
    rows.append(row)

rows = list(reversed(rows))
commit_df = pandas.DataFrame(rows)
backup_times = commit_df["authored_datetime"]


# In[5]:


commit_df.tail(5)


# ## Manual author name fixes

# In[6]:


path = pathlib.Path('renamer.tsv')
renamer = dict()
if path.exists():
    df = pandas.read_csv(path, sep='\t')
    renamer = dict(zip(df.name, df.rename_to))
len(renamer)


# In[7]:


for column in 'author_name', 'committer_name':
    print(f"Unique {column}s before renaming {commit_df[column].nunique()}")
    commit_df[column].replace(renamer, inplace=True)
    print(f"Unique {column}s after renaming {commit_df[column].nunique()}")


# In[8]:


commit_df.head(2)


# In[9]:


# Fix date format to be compatible with R
utc_dt = list()
for index, value in commit_df["authored_datetime"].items():
    utc_dt.append(value.astimezone(pytz.utc))
commit_df["authored_datetime"] = pandas.Series(utc_dt)
commit_df["authored_datetime"] = commit_df["authored_datetime"].dt.date


# ## Export

# In[10]:


commit_df.to_csv('commits.tsv', sep='\t', index=False)


# In[11]:


# Check and see whether these need to be cleaned up!
print(commit_df["author_name"].unique())


# In[12]:


# Go back to the external-resources branch
repo.head.reference = "contrib-viz"


# In[ ]:




