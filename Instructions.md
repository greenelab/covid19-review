# Instructions for Contributing with GitHub

## What is Git?

Have you ever frantically edited a paper, then realized you liked your original version better?
Git is a tool that allows you to track all the changes made to a document over time.
Have you ever been writing something as a team and found that someone was editing an old version of the document?
Git tracks different people's contributions and manages how they get merged together to avoid the headache of figuring out what changed when.

We are managing this project through GitHub with the goal of a) allowing for the manuscript to evolve rapidly as new information comes out, and b) give everyone credit for their attributions.
While we believe this is a great tool, we know it can sometimes be intimidating to get started. 
We don't want the medium to turn anyone away from contributing, so please let us know if you're having problems.


## Most Important: Make a GitHub account

GitHub is an online platform that visualizes changes made with git (think of a really elegant "Track Changes").
You can make an account [here](https://github.com/).
As long as you do this first step of making a GitHub account, you will always be able to open an issue to ask us for help!


## GitHub Vocabulary

- [Repository](http://github.com/greenelab/covid19-review): 
The set of files, issue tracker issues, etc. related to this manuscript 
- [Issue](https://github.com/greenelab/covid19-review/issues): 
The ticketing system for GitHub. 
A ticket can be a question, concern, problem, bug, or anything else you want to bring to the attention of the people working on a repository.
Here, we will use tickets not only for problems or questions, but also to gather papers and preprints that come out about diagnostics and therapeutics related to COVID-19
- Issue Template: 
A way of pre-specifying what an "issue" should look like to be useful. 
We haven't built these yet, but as the project progresses we'll get an idea of what's helpful. 
For now, just try to explain why you're opening the issue (e.g., "I was doing X and ran into problem Y", or "I saw the paper linked here and thought it might be interesting for X reason") 
- [Manuscript Source]( https://github.com/greenelab/covid19-review/tree/master/content): 
The files that comprise the manuscript. 
Right now there's not much here, but we're working on it! 
These are written in a language called ["markdown"](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#lists) which is essentially plain text (thankfully!) 
We have separate a file for each section of the manuscript (Introduction, Diagnostics, and Therapeutics right now).
- [Pull Request](https://github.com/greenelab/covid19-review/pulls): 
A request to change the content of the repository in some way. 
Here, this will usually mean you are adding or editing text.

## How to Contribute

1. Look in the [Manuscript Source]( https://github.com/greenelab/covid19-review/tree/master/content) for the file you want to edit (for example, the [Abstract](https://github.com/greenelab/covid19-review/blob/master/content/01.abstract.md)). 
2. Click the edit button, which looks like a pencil in the upper right corner. 
3. Make any desired changes.
4. Scroll down to the bottom. 
There you will see a section that says "Commit Changes." 
Give your submission a title in the top box and briefly summarize your changes in the bottom box. 
5. Click the box that says "Create a new branch for this commit and start a pull request." 
This will submit a request to add your changes to the underlying document and will notify us to integrate your text into the document!
6. Don't forget to add your information to the [author list](https://github.com/greenelab/covid19-review/blob/master/content/metadata.yaml). 
Copy and update this template:
`-
    github: your_username
    name: your_full_name
    initials: your_initials
    orcid: your_orcid
    twitter: your_twitter
    email: your_email
    contributions:
      - Writing (or modify as needed!) 
    affiliations:
      - Department of XX, University of YY, City, State/Province, Country`
See [manubot](https://github.com/manubot/rootstock/blob/master/content/metadata.yaml) for examples.
You can remove Twitter or ORCID if you don't have an account there (although we strongly encourage making an [ORCID](https://orcid.org/)!)
We will determine author order based on contributions (GitHub tracks who wrote what!)


## Questions

If you are new to GitHub and struggling to follow these directions, we want to know how to help you and how to improve them.
If you find something confusing, please open an issue (as described above) and tell us what you're trying to do, what's going on wrong, or where you're stuck.
We want this review to be a collaborative effort that brings scientists of all skillsets together -- not just people who already know how to use tools like GitHub.
Opening an issue means your question will be available for others to learn from in the future!
It will also us help continually update this document to provide the information people really need as they start contributing.


## A Word of Encouragement
Thanks to GitHub, you won't be able to change anything we can't change back-- so you can't really make a mistake!
