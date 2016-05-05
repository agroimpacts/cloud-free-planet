#! /usr/bin/Rscript
# KMLAccuracyCheck.R
# Main script for calling QAQC accuracy assessment functions
# Author: Lyndon Estes

# Static arguments
prjsrid <- 102022
count.err.wt <- 0.1  
in.err.wt <- 0.7  
out.err.wt <- 0.2  
err.switch <- 1  ### 5/2/2016 Changed to 1
comments <- "F"
write.err.db <- "T"  
draw.maps  <- "T"  
test <- "N"  
test.root <- "N"  
user <- "***REMOVED***"
password <- "***REMOVED***"

suppressMessages(library(rmapaccuracy)) # have to load this to get connection
# suppressMessages(library(sp)) # have to load this to get connection
# suppressMessages(library(RPostgreSQL))

# Test working environment
if(test.root == "Y") {
  prj.sql <- paste0("select proj4text from spatial_ref_sys where srid=", 
                    prjsrid)
  dinfo <- getDBName()  # pull working environment
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, dbname = dinfo["db.name"], user = user, 
                   password = password)
  prjstr <- dbGetQuery(con, prj.sql)$proj4text
  print(paste("database =", dinfo["db.name"], "directory = ", 
              dinfo["project.root"]))
  print(prjstr)
  paste(project.root, "/spatial/R/Error_records/")
  print("Stopping here: Just checking we are working in the right places")
} 

if(test.root == "N") {
  # Input args 
  if(test == "N") {
    arg <- commandArgs(TRUE)
    if(!length(arg) %in% c(3, 4)) stop("3-4 arguments needed", call. = FALSE)
    mtype <- arg[1]  # training "tr" or normal qaqc check "qa"
    kmlid <- arg[2]  # ID of grid cell 
    assignmentid <- arg[3]  # Job identifier
    if(!is.na(arg[4]) & mtype == "tr") tryid <- arg[4] # Try # (training only)
    if(!is.na(arg[4]) & mtype == "qa") {  # qa site have no tryid
      stop("QA tests do not have multiple attempts")
    }
    if(is.na(arg[4]) & mtype == "tr") {  # tr sites need tryid
      stop("Training sites need to have try (attempt) specified")
    }
    if(is.na(arg[4]) & mtype == "qa") {  # set tryid to null for qa sites
      tryid <- NULL
    }
    assignmentidtype <- ifelse(mtype == "tr", "training_id", "assignment_id")
    if(comments == "T") print(mtype)
    if(comments == "T") print(kmlid)
    if(comments == "T") print(assignmentid)
    if(comments == "T") print(tryid)
  }
  
  if(test == "Y") {
    hit.sql <- "select hit_id, name from hit_data"
    hits <- RPostgreSQL::dbGetQuery(con, hit.sql)
    ass.sql <- paste0("select assignment_id, hit_id, worker_id,", 
                      " score from assignment_data")
    asses <- RPostgreSQL::dbGetQuery(con, ass.sql)
    
    if(exists("kmlid") & !exists("assignmentid")) {
      print("Using HIT ID to find assignment ID")
      hid <- hits[hits$name == kmlid, "hit_id"]
      assignmentid <- asses[asses$hit_id == hid, "assignment_id"]
      if(length(assignmentid) > 1) { 
        print(">1 assignment completed for this kml, selecting the first 1")
        assignmentid <- assignmentid[1]
      }
    }
    if(exists("assignmentid") & !exists("kmlid")) {
      print("Using assignment ID to find HIT ID")
      hid <- asses[asses$assignment_id == assignmentid, "hit_id"]
      kmlid <- hits[hits$hit_id == hid, "name"]
    }
  }
  
  KMLAccuracy(mtype = mtype, kmlid = kmlid, assignmentid = assignmentid, 
              tryid = tryid, prjsrid = prjsrid, count.err.wt = count.err.wt, 
              in.err.wt = in.err.wt, out.err.wt = out.err.wt, 
              err.switch = err.switch, comments = comments, 
              write.err.db = write.err.db, draw.maps = draw.maps, test = test,  
              test.root = test.root, user = user, password = password)
}
  
  

