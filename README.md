# COVID-19 review external resources

The `external-resources` branch contains scripts to ingest data from external resources, extract relevant information, and generate figures for the manuscript.
A GitHub Actions workflow in the `master` branch is scheduled to automatically run these scripts to update the external information.
The manuscript on the `master` branch refers to these statistics and figures by URL as if they were in a separate GitHub repository.

## External resources
- `csse`: [COVID-19 Data Repository](https://github.com/CSSEGISandData/COVID-19) by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University
- `ebmdatalab`: [COVID-19 TrialsTracker data](https://github.com/ebmdatalab/covid_trials_tracker-covid) from the Evidence-Based Medicine Data Lab at the University of Oxford
