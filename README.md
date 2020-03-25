# SARS-CoV-2 and COVID-19: An Evolving Review of Diagnostics and Therapeutics

<!-- usage note: edit the H1 title above to personalize the manuscript -->

[![HTML Manuscript](https://img.shields.io/badge/manuscript-HTML-blue.svg)](https://greenelab.github.io/covid19-review/)
[![PDF Manuscript](https://img.shields.io/badge/manuscript-PDF-blue.svg)](https://greenelab.github.io/covid19-review/manuscript.pdf)
[![GitHub Actions Status](https://github.com/greenelab/covid19-review/workflows/Manubot/badge.svg)](https://github.com/greenelab/covid19-review/actions)
[![Gitter](https://badges.gitter.im/covid19-review/community.svg)](https://gitter.im/covid19-review/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
<!-- usage note: delete CI badges above for services not used by your manuscript -->

## Project Description
<!-- usage note: edit this section. -->

With the rapidly evolving global situation related to COVID-19, the infectious disease caused by the SARS-CoV-2 virus, there is a need to centralize scientific knowledge relevant to the development of diagnostics and therapeutics. 
This repository is an online, collaborative review paper written with [manubot](https://manubot.org/). 
We are seeking input from scientists at all levels anywhere in the world.

Our goal is to quickly and accurately summarize and synthesize the papers that are coming out in order to develop a broader picture of what's being attempted and the status of those efforts.
We hope to contextualize elements of this virus and infectious disease with respect to better understood viruses and diseases (e.g., to identify shared mechanisms). 
This repository is also a living document that aims to consolidate and integrate helpful information about diagnostics and therapeutics that is circulating in decentralized spaces (e.g., Twitter threads) into a more permanent and unified format.

## Contributions

You'll need to make a free [GitHub account](https://github.com/join?source=header-home).

Instructions and procedures for contributing are [outlined here](CONTRIBUTING.md).

We will follow the [ICMJE Guidelines](http://www.icmje.org/recommendations/browse/roles-and-responsibilities/defining-the-role-of-authors-and-contributors.html) for determining authorship.

Please note that, while reading scientific literature is a particular skill, we know that people outside of science are also invested in this topic and there is a lot of information circulating about the virus and about possible therapies. 
Non-scientists are welcome to contribute by opening New Paper issues to let us know about topics or papers they're concerned about or would like to see addressed. 

Undergraduate students who are interested are encouraged to take part in discussions, ask questions, post interesting papers, and contribute paper summaries (just please note in your summary that you're a student).

## Pull Requests

If you are not familiar with git and GitHub, you can use [these directions](INSTRUCTIONS.md) to start contributing.

Please feel encouraged to ask questions by opening a [Request for Help issue](https://github.com/greenelab/covid19-review/issues/new?assignees=rando2&labels=&template=request-for-help.md&title=Help%3A+%5BAdd+topic+here%5D)
[![GitHub issues](https://img.shields.io/github/issues-raw/greenelab/covid19-review?label=Open%20Issue&style=social)](https://github.com/greenelab/covid19-review/issues/new/choose)

This project is a collaborative effort that will benefit from the expertise of scientists across a wide range of disciplines!

## Manubot
<!-- usage note: do not edit this section -->

Manubot is a system for writing scholarly manuscripts via GitHub.
Manubot automates citations and references, versions manuscripts using git, and enables collaborative writing via GitHub.
An [overview manuscript](https://greenelab.github.io/meta-review/ "Open collaborative writing with Manubot") presents the benefits of collaborative writing with Manubot and its unique features.
The [rootstock repository](https://git.io/fhQH1) is a general purpose template for creating new Manubot instances, as detailed in [`SETUP.md`](SETUP.md).
See [`USAGE.md`](USAGE.md) for documentation how to write a manuscript.

Please open [an issue](https://git.io/fhQHM) for questions related to Manubot usage, bug reports, or general inquiries.

## Repository directories & files

+ This file is called [`README.md`](README.md)
It is the centralized document for the repository and will help direct users to other relevant information.
+ [`CONTRIBUTING.md`](CONTRIBUTING.md) contains procedures and directions for contributing to this effort.
+ [`INSTRUCTIONS.md`](INSTRUCTIONS.md) contains instructions for new GitHub users for how to navigate GitHub in the browser as well as GitHub vocabulary.
It also includes some instructions for more experienced users about the procedures we recommend and how to run manubot on the command line.
+ [`USAGE.md`](USAGE.md) describes formatting instructions for formatting text, citing references, adding figures and tables, etc.
+ [`SETUP.md`](SETUP.md) includes information about setting up manubot
+ [`LICENSE.md`](LICENSE.md) and [`LICENSE-CC0.md`](LICENSE-CC0.md) contain the licenses associated with manubot and with the content we are developing in this project. Please see the "License" section below.

The directories are as follows:

+ [`content`](content) contains the manuscript source, which includes markdown files as well as inputs for citations and references. 
These are the files that most contributors will be editing.
  See [`USAGE.md`](USAGE.md) for more information.
+ [`output`](output) contains the outputs (generated files) from Manubot including the resulting manuscripts.
  You should not edit these files manually, because they will get overwritten.
+ [`webpage`](webpage) is a directory meant to be rendered as a static webpage for viewing the HTML manuscript.
+ [`build`](build) contains commands and tools for building the manuscript.
+ [`ci`](ci) contains files necessary for deployment via continuous integration.

## License

<!--
usage note: edit this section to change the license of your manuscript or source code changes to this repository.
We encourage users to openly license their manuscripts, which is the default as specified below.
-->

[![License: CC BY 4.0](https://img.shields.io/badge/License%20All-CC%20BY%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by/4.0/)
[![License: CC0 1.0](https://img.shields.io/badge/License%20Parts-CC0%201.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

Except when noted otherwise, the entirety of this repository is licensed under a CC BY 4.0 License ([`LICENSE.md`](LICENSE.md)), which allows reuse with attribution.
Please attribute by linking to https://github.com/manubot/rootstock.

Since CC BY is not ideal for code and data, certain repository components are also released under the CC0 1.0 public domain dedication ([`LICENSE-CC0.md`](LICENSE-CC0.md)).
All files matched by the following glob patterns are dual licensed under CC BY 4.0 and CC0 1.0:

+ `*.sh`
+ `*.py`
+ `*.yml` / `*.yaml`
+ `*.json`
+ `*.bib`
+ `*.tsv`
+ `.gitignore`

All other files are only available under CC BY 4.0, including:

+ `*.md`
+ `*.html`
+ `*.pdf`
+ `*.docx`

Please open [an issue](https://github.com/manubot/rootstock/issues) for any question related to licensing. 
