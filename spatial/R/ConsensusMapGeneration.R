# ConsensusMapGeneration.R
# Main script for calling consensus map generation (Bayes fusion) functions
# Author: Su Ye

# Static arguments
output.heatmap <- FALSE # if output heat map
user <- "***REMOVED***"
password <- "***REMOVED***"
db.tester.name <- "sye"
alt.root <- NULL
host <- NULL
diam <- 0.005 / 2 ## new master grid diameter
conflictpixelthres <- 0.3 # determine conflict pixels that are larger than thres

suppressMessages(library(rmapaccuracy)) # have to load this to get connection

# Input args 
# kmlid <- "ZM1375404" # testlines
# min_mappedcount <- 0 # testlines
# scorethres <- 0     # testlines
# output.conflictmap <- FALSE # testlines
arg <- commandArgs(TRUE)
kmlid <- arg[1]  # ID of grid cell 
min_mappedcount <- arg[2] # minimum mapped map count
scorethres <- arg[3] # score threshold for selecting 'valid' assignment
output.conflictmap <- arg[4] # if output conflict map
if(length(arg) < 4) stop("At least 4 arguments needed", call. = FALSE)
if(length(arg) == 4) {
  output.heatmap <- FALSE
  db.tester.name <- NULL
  alt.root <- NULL
  host <- NULL
} 
if(length(arg) > 4) {
  if(is.na(arg[5])){
    output.heatmap <- FALSE
  } else{
    output.heatmap <- arg[6]
  }
  if(is.na(arg[6])){
    db.tester.name <- NULL
  } else {
    db.tester.name <- arg[6]
  }
  if(is.na(arg[7])) {
    alt.root <- NULL
  } else {
    alt.root <- arg[7]
  } 
  if(is.na(arg[8])) {
    host <- NULL
  } else {
    host <- arg[8]
  }
}

consensusmapcreation(kmlid = kmlid, min_mappedcount = min_mappedcount, 
                     scorethres = scorethres, output.conflictmap = 
                       output.conflictmap, output.heatmap = output.heatmap, 
                     conflictpixelthres  = conflictpixelthres, diam = diam, 
                     user = user, password = password, db.tester.name = 
                       db.tester.name, alt.root = alt.root, host = host)
