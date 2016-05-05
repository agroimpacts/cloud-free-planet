#! /usr/bin/Rscript
##############################################################################################################
# Title      : CheckWorkerAssignment.R
# Purpose    : Script for retrieving worker assignments
# Author     : Lyndon Estes
# Draws from : KMLAccuracyCheck_3.X.R
# Used by    : 
# Notes      : Created 8/10/2013
#              To help respond to Turker tickets
#              Usage: (from terminal) Rscript CheckWorkerAssignment.R kmlid workerid [Y/N]
#               Y or N for testing location/working directory
##############################################################################################################

# Libraries
suppressMessages(library(RPostgreSQL))
suppressMessages(library(rgdal))
suppressMessages(library(rgeos))

# Hardcoded variables
prjsrid <- 97490  # EPSG identifier for equal area project

# Get HIT ID, assignment ID
args <- commandArgs(TRUE)
if(length(args) < 3) stop("Need at least 3 arguments")
hit.id <- args[1]  # "24192NJKM05BS8R9TNN2OTP9E1HFAW" hit.id <- "231TUHYW2GTPFG8M4UNM469Y3YOQL3"
worker.id <- args[2] #  "A1NJ1IJLKAS0Y4" worker.id <- "A2X5DP7XUVYR4P"
test.root <- args[3]

# Find working location
initial.options <- commandArgs(trailingOnly = FALSE)
arg.name <- "--file="
script.name <- sub(arg.name, "", initial.options[grep(arg.name, initial.options)])
script.dir <- dirname(script.name)
source(paste(script.dir, "getDBName.R", sep="/"))
kml.path <- paste0(project.root, "/maps/")
kml.root <- strsplit(project.root, "/")[[1]][3]   

if(test.root == "Y") {
  print(paste("database =", db.name, "; kml.root =", kml.root, "; worker kml directory =", kml.path, 
              "; hit =", hit.id))
  print("Stopping here: Just making sure we are working and writing to the right places")
} 

if(test.root == "N") {
  source(paste(script.dir, "KMLAccuracyFunctions.R", sep="/"))

  # Paths and connections
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, dbname = db.name, user = "***REMOVED***", password = "***REMOVED***")
  
  hit.sql <- paste("select name from hit_data where hit_id='", hit.id, "'", sep = "")
  hits <- dbGetQuery(con, hit.sql)
  ass.sql <- paste("select assignment_id, score from assignment_data where hit_id=", "'", hit.id, 
                   "' and worker_id='", worker.id, "'", sep = "")  
  assignments <- dbGetQuery(con, ass.sql)
  if(nrow(assignments) > 1) stop("More than one assignment for this worker for this HIT")
  
  prj.sql <- paste("select proj4text from spatial_ref_sys where srid=", prjsrid, sep = "")
  prjstr <- dbGetQuery(con, prj.sql)$proj4text
  gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"  # Always this one
  
  # Collect QAQC fields (if there are any; if not then "N" value will be returned). This should work for both
  # training and test sites
  qaqc.sql <- paste("select id,ST_AsEWKT(geom) from qaqcfields where name=", "'", hits$name, "'", sep = "")
  qaqc.geom.tab <- dbGetQuery(con, qaqc.sql)
  qaqc.hasfields <- ifelse(nrow(qaqc.geom.tab) > 0, "Y", "N") 
  if(qaqc.hasfields == "Y") {
    qaqc.geom.tab[, 2] <- gsub("^SRID=*.*;", "", qaqc.geom.tab[, 2])
    qaqc.poly.list <- createCleanTempPolyfromWKT(geom.tab = qaqc.geom.tab, crs = prjstr)
    qaqc.poly <- qaqc.poly.list[[1]]
    qaqc.poly@data$ID <- rep(qaqc.geom.tab[1, 1], nrow(qaqc.poly))
    qaqc.poly@data$fld <- 1:nrow(qaqc.poly@data)
    qaqc.poly@data <- qaqc.poly@data[, -1]
  } 

  # Read in user data
  user.sql <- paste("select name,ST_AsEWKT(geom) from user_maps where assignment_id=", "'", 
                    assignments$assignment_id, "'", " order by name", sep = "")  
  user.geom.tab <- dbGetQuery(con, user.sql)  # Collect user data and fields geometries
  #user.geom.tab <- user.geom.tab[grep(hits$name, user.geom.tab$name), ]  # added to drop other training results
  user.hasfields <- ifelse(nrow(user.geom.tab) > 0, "Y", "N")  # Need to get this right
  if(user.hasfields == "Y") {  # Read in user fields if there are any
    user.geom.tab[, 2] <- gsub("^SRID=*.*;", "", user.geom.tab[, 2])
    user.poly.list <- createCleanTempPolyfromWKT(geom.tab = user.geom.tab, crs = gcs)
    user.poly <- user.poly.list[[1]]
    user.poly@data$ID <- rep(user.geom.tab[1, 1], nrow(user.poly))
    user.poly@data$fld <- 1:nrow(user.poly@data)
    user.poly@data <- user.poly@data[, -1]
  }

  # Create unique directory for worker if file doesn't exist
  worker.path <- paste(kml.path, worker.id, sep = "")
  if(!file.exists(worker.path)) dir.create(path = worker.path)
  
  # Write KMLs out to worker specific directory
  setwd(worker.path)
  if(exists("user.poly")) {
    user.poly@data$kmlname <- paste(hits$name, "_w", sep = "")  
    writeOGR(user.poly, dsn = paste(user.poly@data$kmlname, "kml", sep = "."), 
             layer = user.poly@data$kmlname, driver = "KML", dataset_options = c("NameField = name"), 
             overwrite = TRUE)  # Write it
  }
  if(exists("qaqc.poly")) {
    qaqc.poly.gcs <- spTransform(x = qaqc.poly, CRSobj = CRS(gcs))  # First convert to geographic coords
    qaqc.poly.gcs@data$kmlname <- paste(hits$name, "_r", sep = "")
    writeOGR(qaqc.poly.gcs, dsn = paste(qaqc.poly.gcs@data$kmlname[1], "kml", sep = "."), 
             layer = qaqc.poly.gcs@data$kmlname, driver = "KML", dataset_options = c("NameField = name"), 
             overwrite = TRUE)  # Write it
  }
  worker.url <- paste("http://", kml.root, ".princeton.edu/api/getkml?workerId=", worker.id, "&kmlName=", 
                      hits$name, sep = "")
  cat(worker.url, "\n") # Return details
}
