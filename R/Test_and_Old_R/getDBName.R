#! /usr/bin/R -f
##############################################################################################################
# Title      : getDBName.R
# Purpose    : Extract the correct database name from the working environment, for use by Rscripts
# Author     : Lyndon Estes
# Draws from : 
# Used by    : KMLAccuracyCheck.R; KMLGenerate.R
# Notes      : Created 26/9/2013
#                    
##############################################################################################################

db.sandbox.name <- 'SouthAfricaSandbox'
db.production.name <- 'SouthAfrica'

info <- Sys.info()
euser <- unname(info["effective_user"])
if(euser == "sandbox") {
  sandbox <- TRUE
  uname <- "sandbox"
} else if(euser == "mapper") {
  sandbox <- FALSE
  uname <- "mapper"
} else {
  stop("Any R script must run under sandbox or mapper user")
}

project.root <- paste("/u/", uname, "/afmap", sep = "")  # Project root path

if(sandbox == TRUE) {
  db.name <- db.sandbox.name
} else {
  db.name <- db.production.name
}

rm(sandbox, euser, info, db.sandbox.name, db.production.name)
