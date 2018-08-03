# consensus_map_generator.R
# Main script for calling consensus map generation (Bayes Averaging) functions
# Author: Su Ye

# Static arguments
output.heatmap <- FALSE # if output heat map
user <- "***REMOVED***"
password <- "***REMOVED***"
diam <- 0.005 / 2 # new master grid diameter
riskpixelthres <- 0.4 # determine risky pixels that are larger than threshold
suppressMessages(library(rmapaccuracy)) # have to load this to get connection

# Input args 
# kmlid <- "GH0588012" # testlines
# min.mappedcount <- 0 # testlines
# scorethres <- 0     # testlines
# output.riskmap <- FALSE # testlines
# db.tester.name <- 'sye' # testlines
# alt.root <- NULL # testlines
# host <- NULL # testlines

if(length(arg) < 2) stop("At least 2 arguments needed", call. = FALSE)
arg <- commandArgs(TRUE)
kmlid <- arg[1]  # ID of grid cell 
min.mappedcount <- arg[2] # minimum mapped map count
if(length(arg) == 2) {
  output.riskmap <- FALSE
  db.tester.name <- NULL
  alt.root <- NULL
  host <- NULL
} 
if(length(arg) > 2) {
  if(is.na(arg[3])){
    output.riskmap <- FALSE
  } else{
    output.riskmap <- arg[3]
  }
  if(is.na(arg[4])){
    db.tester.name <- NULL
  } else {
    db.tester.name <- arg[4]
  }
  if(is.na(arg[5])) {
    alt.root <- NULL
  } else {
    alt.root <- arg[5]
  } 
  if(is.na(arg[6])) {
    host <- NULL
  } else {
    host <- arg[6]
  }
}

consensus_map_creation(kmlid = kmlid, min.mappedcount = min.mappedcount, 
                       output.riskmap = output.riskmap,
                       riskpixelthres  = riskpixelthres, diam = diam, 
                       user = user, password = password, 
                       db.tester.name = db.tester.name, 
                       alt.root = alt.root, host = host)
