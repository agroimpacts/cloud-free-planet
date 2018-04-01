#! /usr/bin/Rscript
################################################################################
# Title      : CheckWorkerAssignment.R
# Purpose    : Script for retrieving worker assignments
# Author     : Lyndon Estes
# Draws from : KMLAccuracyCheck_3.X.R
# Used by    : 
# Notes      : Created 8/10/2013
#              To help respond to Turker tickets
#              Usage: (from terminal) Rscript CheckWorkerAssignment.R kmlid 
#               workerid [Y/N]
#               Y or N for testing location/working directory
################################################################################

# Libraries
# suppressMessages(library(RPostgreSQL))
suppressMessages(library(rmapaccuracy))

# Hardcoded variables
prjsrid <- 102022  # EPSG identifier for equal area project

# Get HIT ID, assignment ID
args <- commandArgs(TRUE)
if(length(args) < 3) stop("Need at least 3 arguments")
hit.id <- args[1]  # hit.id <- '3SNR5F7R92TY0D6DE7O1VJ1MKE5IEK'
worker.id <- args[2] #  worker.id <- "A2X5DP7XUVYR4P"
test.root <- args[3]  # test.root <- "Y"

# Find working location
dinfo <- getDBName()  # pull working environment

initial.options <- commandArgs(trailingOnly = FALSE)
# arg.name <- "--file="
# script.name <- sub(arg.name, "", 
#                    initial.options[grep(arg.name, initial.options)])
# script.dir <- dirname(script.name)
# source(paste(script.dir, "getDBName.R", sep="/"))
kml.path <- paste0(dinfo["project.root"], "/maps/")
kml.root <- strsplit(dinfo["project.root"], "/")[[1]][3]   

if(test.root == "Y") {
  print(paste("database =", dinfo["db.name"], "; kml.root =", kml.root, 
              "; worker kml directory =", kml.path, "; hit =", hit.id))
  print(paste("Stopping here: Just making sure we are working and writing to", 
              "the right places"))
} 

if(test.root == "N") {
#   source(paste(script.dir, "KMLAccuracyFunctions.R", sep="/"))

  # Paths and connections
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                   password = "***REMOVED***")
  
  hit.sql <- paste0("select name from hit_data where hit_id='", hit.id, "'")
  hits <- dbGetQuery(con, hit.sql)
  ass.sql <- paste0("select assignment_id, score from assignment_data where ", 
                   "hit_id=", "'", hit.id, "' and worker_id='", worker.id, "'")  
  assignments <- dbGetQuery(con, ass.sql)
  if(nrow(assignments) > 1) {
    stop("More than one assignment for this worker for this HIT")
  }
  
  prj.sql <- paste0("select proj4text from spatial_ref_sys where srid=", 
                    prjsrid)
  prjstr <- dbGetQuery(con, prj.sql)$proj4text
  # Always this one
  gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
  
  # Collect QAQC fields (if there are any; if not then "N" value will be 
  # returned). This should work for both
  # training and test sites
  qaqc.sql <- paste("select id,ST_AsEWKT(geom) from qaqcfields", "
                    where name=", "'", hits$name, "'", sep = "")
  qaqc.geom.tab <- dbGetQuery(con, qaqc.sql)
  qaqc.hasfields <- ifelse(nrow(qaqc.geom.tab) > 0, "Y", "N") 
  if(qaqc.hasfields == "Y") {
    qaqc.geom.tab[, 2] <- gsub("^SRID=*.*;", "", qaqc.geom.tab[, 2])
    qaqc.poly <- polyFromWkt(geom.tab = qaqc.geom.tab, crs = prjstr)
    # qaqc.poly <- qaqc.poly.list[[1]]
    qaqc.poly@data$ID <- rep(1, nrow(qaqc.poly))
    qaqc.poly@data$fld <- 1:nrow(qaqc.poly@data)
    qaqc.poly@data <- qaqc.poly@data[, -1]
  } 

  # Read in user data
  user.sql <- paste0("select name,ST_AsEWKT(geom) from user_maps where ", 
                     "assignment_id=", "'", assignments$assignment_id, "'", 
                     " order by name")  
  user.geom.tab <- dbGetQuery(con, user.sql)  # Collect user data & field geoms
  user.hasfields <- ifelse(nrow(user.geom.tab) > 0, "Y", "N")  # get this right
  if(user.hasfields == "Y") {  # Read in user fields if there are any
    user.geom.tab[, 2] <- gsub("^SRID=*.*;", "", user.geom.tab[, 2])
    user.poly <- polyFromWkt(geom.tab = user.geom.tab, crs = gcs)
    # user.poly <- user.poly.list[[1]]
    user.poly@data$ID <- rep(1, nrow(user.poly))
    user.poly@data$fld <- 1:nrow(user.poly@data)
    user.poly@data <- user.poly@data[, -1]
  }

  # Create unique directory for worker if file doesn't exist
  worker.path <- paste(kml.path, worker.id, sep = "")
  if(!file.exists(worker.path)) dir.create(path = worker.path)
  
  # Write KMLs out to worker specific directory
  setwd(worker.path)
  if(exists("user.poly")) {  # Write it
    user.poly@data$kmlname <- paste0(hits$name, "_w")  
    writeOGR(user.poly, dsn = paste0(hits$name, "_w.kml"), 
             layer = paste0(hits$name, "_w"), driver = "KML", 
             dataset_options = c("NameField = name"), overwrite = TRUE)  
  }
  if(exists("qaqc.poly")) {  # First convert to geographic coords
    qaqc.poly.gcs <- spTransform(x = qaqc.poly, CRSobj = CRS(gcs))  
    qaqc.poly.gcs@data$kmlname <- paste0(hits$name, "_r")
    writeOGR(qaqc.poly.gcs,  # Write it
             dsn = paste0(hits$name, "_r.kml"), 
             layer = paste0(hits$name, "_r"), driver = "KML", 
             dataset_options = c("NameField = name"), overwrite = TRUE) 
  }
  worker.url <- paste0("http://", kml.root, 
                       ".princeton.edu/api/getkml?workerId=", worker.id, 
                       "&kmlName=", hits$name)
  cat(worker.url, "\n") # Return details
}
