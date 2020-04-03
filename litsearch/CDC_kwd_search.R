#!/usr/bin/env Rscript

# Created by Halie Rando (GitHub: rando2) on April 2, 2020 for COVID-19 Review
# https://github.com/greenelab/covid19-review

# May require this version of Rcpp to run on a Mac:
# install.packages("Rcpp", repos="https://RcppCore.github.io/drat")

# Load libraries and set encoding ----------

library("Rcpp")
library("readxl") #installs with tidyverse
library("httr")
suppressPackageStartupMessages(library("tidyverse"))
encoding = "utf-8"

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
      download.file(remote_fname, destfile = local_fname, quiet = TRUE)
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

findpapers <- function (COVID19_data, keywords){
  # Use a vector of keywords to identify papers that may be relevant
  # to a particular therapeutic. Therapeutic name should be first keyword.
  # Searches papers' title, abstract, and keywords.
  # Currently, keywords are assumed to be single words
  # Accepts: CDC paper information as dataframe, keywords as vector
  # Returns: Null (csv file is written instead)
  
  # Modify keywords to be case-independent (e.g., "[Rr]emdesivir")
  # Note: as of Apr 3 2020, no all-caps in the CDC reference document
  alt_kw <- paste("[", toupper(substr(keywords, 1, 1)), 
                tolower(substr(keywords, 1, 1)), "]", 
                substr(keywords, 2, 100), sep="") 
  
  # Search CDC paper Title, Abstract, Keywords for the specified keywords
  # Write matches to CSV file named for therapeutic and date run
  hit_papers <- COVID19_data %>%
    select(c("Date Added", "Title", "DOI", "Year", "Journal/Publisher",
             "Abstract", "Keywords", "URL")) %>% 
    filter(str_detect(Abstract, paste(alt_kw, collapse = '|')) | 
            str_detect(Title, paste(alt_kw, collapse = '|')) | 
            str_detect(Keywords, paste(alt_kw, collapse = '|')) 
           ) 
  #write.table(hit_papers, file.path("bytopic", paste(keywords[1], Sys.Date(), "csv", sep=".")), 
            #row.names = FALSE, fileEncoding = "UTF-8")
  return(hit_papers)
}

# Run keyword searches for therapeutics ---------------------

# Create dataframe containing most recent CDC data
# Optional argument of data as "YYYY-MM-DD" if alt date needed
COVID19_data <- getdata()

# Below, for each therapeutic, call findpapers
# Must specify dataframe with CDC data (COVID19_data) and vector of keywords
# The therapeutic itself should be the first keyword
# Assumes each keyword is one word and < 100 characters. 
# Avoid unnecessary capitalization
# Each call of findpapers() will generate a separate csv output file
print(findpapers(COVID19_data, 
                 c("Remdesivir", "GS-5734", "GS-441524", "adenosine"))) 
