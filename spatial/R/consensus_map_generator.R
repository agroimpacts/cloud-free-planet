# consensus_map_generator.R
# Main script for calling consensus map generation (Bayes Averaging) functions
# Author: Su Ye

# Static arguments
diam <- 0.005 / 2 # new master grid diameter
suppressMessages(library(rmapaccuracy)) # have to load this to get connection

# Input args 
# kmlid <- "GH0075752" # testlines
# output.riskmap <- FALSE # testlines
# host <- NULL # testlines

arg <- commandArgs(TRUE)
kmlid <- arg[1]  # ID of grid cell

## legacy of previous version, and may delete in future
kml.usage <- arg[2] # the use of kml, could be 'train, 'validate' or 'holdout'

if(length(arg) < 2) stop("At least 2 arguments needed", call. = FALSE)
if(length(arg) == 2) {
  output.riskmap <- FALSE
  host <- NULL
} 
if(length(arg) > 2) {
  if(is.na(arg[3])){
    output.riskmap <- FALSE
  } else{
    output.riskmap <- arg[3]
  }
  if(is.na(arg[4])) {
    host <- NULL
  } else {
    host <- arg[4]
  }
}

consensus_map_creation(kmlid = kmlid, kml.usage = kml.usage, 
                       output.riskmap = output.riskmap,
                       diam = diam, host = host)
