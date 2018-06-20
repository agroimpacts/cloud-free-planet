# consensus_map_generator.R
# Main script for calling consensus map generation (Bayes fusion) functions
# Author: Su Ye

# Static arguments
output.heatmap <- FALSE # if output heat map
user <- "***REMOVED***"
password <- "***REMOVED***"
diam <- 0.005 / 2 ## new master grid diameter
riskpixelthres <- 0.4 # determine risky pixels that are larger than thres

suppressMessages(library(rmapaccuracy)) # have to load this to get connection

# Input args 
# kmlid <- "ZM1375404" # testlines
# min_mappedcount <- 0 # testlines
# scorethres <- 0     # testlines
# output.riskmap <- FALSE # testlines
# db.tester.name <- 'sye'
# alt.root <- NULL
# host <- NULL

if(length(arg) < 3) stop("At least 3 arguments needed", call. = FALSE)
arg <- commandArgs(TRUE)
kmlid <- arg[1]  # ID of grid cell 
min_mappedcount <- arg[2] # minimum mapped map count
# score threshold for selecting 'valid' assignments for merging consensus
scorethres <- arg[3] 
if(length(arg) == 3) {
  output.riskmap <- FALSE
  db.tester.name <- NULL
  alt.root <- NULL
  host <- NULL
} 
if(length(arg) > 3) {
  if(is.na(arg[4])){
    output.riskmap <- FALSE
  } else{
    output.riskmap <- arg[4]
  }
  if(is.na(arg[5])){
    db.tester.name <- NULL
  } else {
    db.tester.name <- arg[5]
  }
  if(is.na(arg[6])) {
    alt.root <- NULL
  } else {
    alt.root <- arg[6]
  } 
  if(is.na(arg[8])) {
    host <- NULL
  } else {
    host <- arg[8]
  }
}

consensus_map_creation(kmlid = kmlid, min_mappedcount = min_mappedcount, 
                       scorethres = scorethres, output.riskmap = output.riskmap,
                       riskpixelthres  = riskpixelthres, diam = diam, 
                       user = user, password = password, 
                       db.tester.name = db.tester.name, 
                       alt.root = alt.root, host = host)
