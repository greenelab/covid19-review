# COVID-19 review external resources

The `external-resources` branch contains scripts to ingest data from external resources, extract relevant information, and generate figures for the manuscript.
A GitHub Actions workflow in the `master` branch is scheduled to automatically run these scripts to update the external information.
The manuscript on the `master` branch refers to these statistics and figures by URL as if they were in a separate GitHub repository.

## External resources
- `CORD-19`: [COVID-19 Open Research Dataset Challenge](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge) (CORD-19) with AI2, CZI, MSR, Georgetown, NIH and The White House
- `csse`: [COVID-19 Data Repository](https://github.com/CSSEGISandData/COVID-19) by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University
- `ebmdatalab`: [COVID-19 TrialsTracker data](https://github.com/ebmdatalab/covid_trials_tracker-covid) from the Evidence-Based Medicine Data Lab at the University of Oxford
- `owiddata`: [Data on COVID-19 (coronavirus)](https://github.com/owid/covid-19-data) by Our World in Data, see <https://ourworldindata.org/coronavirus> for details and attribution
- `version-figures.sh`: a script that updates the JSON statistics files to use the versioned figure URLs
