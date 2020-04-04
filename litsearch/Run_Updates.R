library("knitr")
source("R_Functions/CDC_query_functions.R")

# Go to CDC website and download the most recent list of papers
COVID19_data <- getdata()
print(paste("Database last updated at", Sys.time(), "and contains", 
            nrow(COVID19_data), "papers"))

# Read in keyword lists. Treatment name should be first keyword.
for (line in readLines("keywords.txt")){
  keywords <- str_split(line, ", ", simplify=TRUE)
  findpapers(COVID19_data, keywords)
  template <- read_file('./bytopic/TEMPLATE.Rmd')
  md_file <- gsub("KEYWORD", keywords[1], template)
  md_file <- gsub("RUNDATE", Sys.time(), md_file)
  md_file <- gsub("ALLKW", line, md_file)
  write_file(md_file, file.path("bytopic/", paste(keywords[1], "Rmd", sep=".")))
  system(paste("cd bytopic; ls; R -e \"rmarkdown::render('", 
               paste(keywords[1]),
               ".Rmd',output_file='",
               paste(keywords[1]),
               ".html')\"", sep=""))
}
