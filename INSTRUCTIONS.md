# Instructions for Contributing with GitHub

## Instructions for New Users

If you are new to GitHub or would prefer to work in your browser, please follow the directions in this section.

### What is Git?

Have you ever frantically edited a paper, then realized you liked your original version better?
Git is a tool that allows you to track all the changes made to a document over time.
Have you ever been writing something as a team and found that someone was editing an old version of the document?
Git tracks different people's contributions and manages how they get merged together to avoid the headache of figuring out what changed when.

We are managing this project through GitHub with the goal of a) allowing for the manuscript to evolve rapidly as new information comes out, and b) give everyone credit for their contributions.
While we believe this is a great tool, we know it can sometimes be intimidating to get started. 
We don't want the medium to turn anyone away from contributing, so please let us know if you're having problems.

### Most Important: Make a GitHub account

GitHub is an online platform that visualizes changes made with git (think of a really elegant "Track Changes").
You can make an account [here](https://github.com/).
As long as you do this first step of making a GitHub account, you will always be able to open an issue to ask us for help!

### GitHub Vocabulary

- [Repository](http://github.com/greenelab/covid19-review): 
The set of files, issue tracker issues, etc. related to this manuscript 
- [Issue](https://github.com/greenelab/covid19-review/issues): 
The ticketing system for GitHub. 
A ticket can be a question, concern, problem, bug, or anything else you want to bring to the attention of the people working on a repository.
Here, we will use tickets not only for problems or questions, but also to gather papers and preprints that come out about diagnostics and therapeutics related to COVID-19
- Issue Template: 
A way of pre-specifying what an "issue" should look like to be useful. 
There might be a template that fits your needs (e.g., New Paper, or asking for help with GitHub).
If not, just try to explain why you're opening the issue (e.g., "I was doing X and ran into problem Y", or "I saw the paper linked here and thought it might be interesting for X reason") 
- [Manuscript Source]( https://github.com/greenelab/covid19-review/tree/master/content): 
The files that comprise the manuscript. 
These are located in the "content" folder that you see. 
These are written in a language called ["markdown"](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#lists) which is essentially plain text (thankfully!) 
We have separate a file for each section of the manuscript (Introduction, Pathogenesis, Diagnostics, and Therapeutics right now).
- [Pull Request](https://github.com/greenelab/covid19-review/pulls) or PR: 
A request to change the content of the repository in some way. 
Here, this will usually mean you are adding or editing text.

### How to Make a Pull Request

1. Look in the [Manuscript Source]( https://github.com/greenelab/covid19-review/tree/master/content) for the file you want to edit (for example, the [Abstract](https://github.com/greenelab/covid19-review/blob/master/content/01.abstract.md)). 
2. Click the edit button, which looks like a pencil in the upper right corner. 
3. Make any desired changes.
4. Scroll down to the bottom. 
There you will see a section that says "Commit Changes." 
Give your submission a title in the top box and briefly summarize your changes in the bottom box. 
5. Click the box that says "Create a new branch for this commit and start a pull request." 
This will submit a request to add your changes to the underlying document and will notify us to integrate your text into the document!
6. Don't forget to [add your information to the author list](https://github.com/greenelab/covid19-review/blob/master/Contributing.md). 
If you don't have an ORCID, you can make one [here](https://orcid.org/).

### Questions

If you are new to GitHub and struggling to follow these directions, we want to know how to help you and how to improve them.
If you find something confusing, please open an issue (as described above) and tell us what you're trying to do, what's going on wrong, or where you're stuck.
We want this review to be a collaborative effort that brings scientists of all skillsets together -- not just people who already know how to use tools like GitHub.
Opening an issue means your question will be available for others to learn from in the future!
It will also us help continually update this document to provide the information people really need as they start contributing.

### A Word of Encouragement
Thanks to GitHub, you won't be able to change anything we can't change back-- so you can't really make a mistake!

## Command Line Users

### Pull Request Instructions

If you're already someone who uses Git, you can instead:
1. Fork the repository [greenelab/covid19-review](https://github.com/greenelab/covid19-review)
[![GitHub forks](https://img.shields.io/github/forks/greenelab/covid19-review?label=Fork&style=social)](https://github.com/greenelab/covid19-review/fork)
2. Push your modifications.
If writing full paragraphs, please put one sentence per line.
3. Submit a pull request to add your changes to [greenelab/covid19-review](https://github.com/greenelab/covid19-review)
4. Submit a second pull request to add your information to the bottom of the [metadata file](content/metadata.yaml) using the format outlined [here](https://github.com/manubot/rootstock/blob/master/content/metadata.yaml)

### Local execution

The easiest way to run Manubot is to use [continuous integration](#continuous-integration) to rebuild the manuscript when the content changes.
If you want to build a Manubot manuscript locally, install the [conda](https://conda.io) environment as described in [`build`](build).
Then, you can build the manuscript on POSIX systems by running the following commands from this root directory.

```sh
# Activate the manubot conda environment (assumes conda version >= 4.4)
conda activate manubot

# Build the manuscript, saving outputs to the output directory
bash build/build.sh

# At this point, the HTML & PDF outputs will have been created. The remaining
# commands are for serving the webpage to view the HTML manuscript locally.
# This is required to view local images in the HTML output.

# Configure the webpage directory
manubot webpage

# You can now open the manuscript webpage/index.html in a web browser.
# Alternatively, open a local webserver at http://localhost:8000/ with the
# following commands.
cd webpage
python -m http.server
```

Sometimes it's helpful to monitor the content directory and automatically rebuild the manuscript when a change is detected.
The following command, while running, will trigger both the `build.sh` script and `manubot webpage` command upon content changes:

```sh
bash build/autobuild.sh
```
### Continuous Integration

Whenever a pull request is opened, CI (continuous integration) will test whether the changes break the build process to generate a formatted manuscript.
The build process aims to detect common errors, such as invalid citations.
If your pull request build fails, see the CI logs for the cause of failure and revise your pull request accordingly.

When a commit to the `master` branch occurs (for example, when a pull request is merged), CI builds the manuscript and writes the results to the [`gh-pages`](https://github.com/manubot/rootstock/tree/gh-pages) and [`output`](https://github.com/manubot/rootstock/tree/output) branches.
The `gh-pages` branch uses [GitHub Pages](https://pages.github.com/) to host the following URLs:

+ **HTML manuscript** at https://greenelab.github.io/covid19-review/
+ **PDF manuscript** at https://greenelab.github.io/covid19-review/manuscript.pdf

For continuous integration configuration details, see [`.github/workflows/manubot.yaml`](.github/workflows/manubot.yaml) if using GitHub Actions or [`.travis.yml`](.travis.yml) if using Travis CI.

