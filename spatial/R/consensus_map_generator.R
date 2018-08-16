# consensus_map_generator.R
# Main script for calling consensus map generation (Bayes Averaging) functions
# Author: Su Ye

# Static arguments
output.heatmap <- FALSE # if output heat map
diam <- 0.005 / 2 # new master grid diameter
riskpixelthres <- 0.4 # determine risky pixels that are larger than threshold
suppressMessages(library(rmapaccuracy)) # have to load this to get connection

# Input args 
# kmlid <- "GH0067266" # testlines
# min.mappedcount <- 0 # testlines
# scorethres <- 0     # testlines
# output.riskmap <- FALSE # testlines
# db.tester.name <- 'sye' # testlines
# alt.root <- NULL # testlines
# host <- NULL # testlines

arg <- commandArgs(TRUE)
kmlid <- arg[1]  # ID of grid cell
kml.usage <- arg[2] # the use of kml, could be 'train, 'validate' or 'holdout'
min.mappedcount <- arg[3] # minimum mapped map count
if(length(arg) < 3) stop("At least 3 arguments needed", call. = FALSE)
if(length(arg) == 3) {
  output.riskmap <- FALSE
  host <- NULL
} 
if(length(arg) > 3) {
  if(is.na(arg[4])){
    output.riskmap <- FALSE
  } else{
    output.riskmap <- arg[4]
  }
  if(is.na(arg[5])) {
    host <- NULL
  } else {
    host <- arg[5]
  }
}

consensus_map_creation(kmlid = kmlid, kml.usage = kml.usage, 
                       min.mappedcount = min.mappedcount, 
                       output.riskmap = output.riskmap,
                       riskpixelthres = riskpixelthres, diam = diam, 
                       host = host)
