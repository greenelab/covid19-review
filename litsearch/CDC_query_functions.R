#!/usr/bin/env Rscript

# Initialize Database of CDC COVID-19 Literature Dataset
# Created by Halie Rando (GitHub: rando2) on April 3, 2020 for COVID-19 Review
# https://github.com/greenelab/covid19-review

# May require this version of Rcpp to run on a Mac:
# install.packages("Rcpp", repos="https://RcppCore.github.io/drat")

# Load libraries ----------
library("Rcpp")
library("readxl") #installs with tidyverse
library("httr")
library("readr")
suppressPackageStartupMessages(library("tidyverse"))

# Function definitions ---------------------

getdata <- function (query_date = Sys.Date()){
  # Retrieves paper data from most recent Excel file on CDC website
  # Accepts: date or default to today's date
  # Returns: dataframe with most recent CDC paper list as of [date]
  
  # To start, no data has been retrieved
  data_retrieved = FALSE 
  
  # Because CDC updates M-F in evening, work backwards to find most recent data
  while (data_retrieved == FALSE){ 
    # data_retrieved is set to false until a file is found. 
    # Then set to the name of the downloaded file (date-dependent value)
    data_retrieved = readURL(query_date)
    query_date = query_date - 1
  }
  
  # Load in data from CDC's Excel file (R will try to take 4 extra col)
  COVID19_data <- read_excel(data_retrieved, 
                             col_types = c("date", "text", "text", 
                                           "text", "text", "text", "text", 
                                           "text", "text", "text", "text", 
                                           "text", "text", "text", "text", 
                                           "text", "skip", "skip", 
                                           "skip", "skip"), 
                             progress = FALSE)

  # Clean up some formatting issues
  names(COVID19_data)[c(1,10,13,14)] <- c("DateAdded", "AccessionNumber",
                                          "NameOfDatabase", "DatabaseProvider")
  COVID19_data[,1] <- as.Date(COVID19_data$DateAdded)
  
  # Return dataframe of all data from CDC's most recent Excel file
  return (COVID19_data) 
}

readURL <- function (query_date) {
  # Query CDC website for Excel file corresponding to specific date
  # Accepts: date as "YYYY-MM-DD"
  # Returns: either FALSE (if not found) or name of file (if found)
  
  # The local and remote filenames are determined by date
  # Remote uses nonstandard date format, some tricks required
  local_fname <- paste("CDC-COVID19-pubs", query_date, "xlsx", sep = ".")
  remote_date <- paste(as.character(as.numeric(format(query_date, "%d"))),
                       format(query_date, "%B%Y"), sep="")
  remote_fname <- paste("https://www.cdc.gov/library/docs/covid19/COVID19_Excel_",
                        remote_date, ".xlsx", sep="")
  
  # Attempt to download the data for the date from the CDC website
  # If file is downlaoded, return local_fname, else return FALSE
  out <- tryCatch ( 
    {
      download.file(remote_fname, destfile = local_fname) #, quiet = TRUE)
      return (local_fname) 
    },
    error = function (cond) {
      return (FALSE)
    },
    warning = function (cond) {
      return (FALSE)
    }
  )    
}

findpapers <- function (keywords){
  # Use a vector of keywords to identify papers that may be relevant
  # to a particular therapeutic. Therapeutic name should be first keyword.
  # Searches papers' title, abstract, and keywords.
  # Currently, keywords are assumed to be single words
  # Accepts: CDC paper information as dataframe, keywords as vector
  # Returns: Null (csv file is written instead)
  
  # Modify keywords to be case-independent (e.g., "[Rr]emdesivir")
  alt_kw <- paste("[", toupper(substr(keywords, 1, 1)), 
                  tolower(substr(keywords, 1, 1)), "]", 
                  substr(keywords, 2, 100), sep="") 
  
  # Search CDC paper Title, Abstract, Keywords for the specified keywords
  hit_papers <- COVID19_data %>%
    select(c("DateAdded", "Title", "DOI", "Year", "Journal/Publisher",
             "Abstract", "Keywords", "URL")) %>% 
    filter(str_detect(Abstract, paste(alt_kw, collapse = '|')) | 
             str_detect(Title, paste(alt_kw, collapse = '|')) | 
             str_detect(Keywords, paste(alt_kw, collapse = '|')) 
    ) 
  hit_papers <- cbind(hit_papers, data.frame("Issue" = rep("",nrow(hit_papers)),
                               "Reviewers" = rep("",nrow(hit_papers)),
                               "PRs" = rep("", nrow(hit_papers))))
  write_tsv(hit_papers, 
            file.path("bytopic", paste(keywords[1], Sys.Date(), "tsv", sep=".")))
  print(paste("There are", nrow(hit_papers), "papers about", keywords[1], "as of", 
              Sys.time()))
}