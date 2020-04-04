library("Rcpp")
library("readxl") #installs with tidyverse
library("httr")
library("readr")
suppressPackageStartupMessages(library("tidyverse"))

topicCheck <- function(topic){
  query_date <- Sys.Date()
  data_file <- NULL
  while (is.null(data_file)) {
    filename <- paste(topic, query_date, "tsv", sep=".")
    if (file.exists(filename)){
      data_file <- filename
      return(data_file)
    } else if (as.numeric(format(query_date, "%y")) < 2020){
      print("Problem: this therapeutic hasn't been initialized")
      break
    }
    else{
      query_date <- query_date - 1
    }
  }
}

addInfo <- function(target, new_info, update_col) {
  if (length(target$update_col) == 0) {
    return(new_info)
  } else {
    return(paste(target$update_col, new_info, sep=","))
  }
}

addData <- function(topic_data, title, issue, reviewer, pull_request, file_name) {
  target <- topic_data[which(topic_data$Title == "title"), ]
  if (nrow(target) != 1){
    print("Something is wrong with the title")
  } else {
    if (length(issue) > 0) {
      target$Issue <- addInfo(target, issue, "Issue")
    }
    if (length(reviewer) > 0) {
      target$Reviewers <- addInfo(target, reviewer, "Reviewer")
    }
    if (length(pull_request) > 0){
      target$PRs <- addInfo(target, pull_request, "PRs")
    }
  }
  topic_data[which(topic_data$Title == "title"), ] <- target
  write_tsv(topic_data, file_name)
}