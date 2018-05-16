#! /usr/bin/Rscript
# KMLAccuracyCheck.R
# Main script for calling QAQC accuracy assessment functions
# Author: Lyndon Estes

# Static arguments
diam <- 0.005 / 2 ## new master grid diameter
prjsrid <- 102022
count.acc.wt <- 0.1
in.acc.wt <- 0.7  
out.acc.wt <- 0.2  
new.in.acc.wt <- 0.6 ## for new score
new.out.acc.wt <- 0.2 ## for new score
frag.acc.wt <- 0.1 ## for new score
edge.acc.wt <- 0.1 ## for new score
edge.buf <- 9 ## for new score, 3 planet pixels
# err.switch <- 1  ### 5/2/2016 Changed to 1
acc.switch <- 1  ### 5/2/2016 Changed to 1
comments <- "F"
write.acc.db <- "T"  
draw.maps  <- "T"  
test <- "N"  
test.root <- "N"  
alt.root <- NULL
host <- NULL
pngout <- TRUE
user <- "***REMOVED***"
password <- "***REMOVED***"

suppressMessages(library(rmapaccuracy)) # have to load this to get connection

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
  print(paste0(dinfo["project.root"], "/spatial/R/Error_records/"))  # fix this, because it won't work
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
  
  kml_accuracy(mtype = mtype, kmlid = kmlid, assignmentid = assignmentid,
               diam = diam, tryid = tryid, prjsrid = prjsrid, 
               count.acc.wt = count.acc.wt, in.acc.wt = in.acc.wt, 
               out.acc.wt = out.acc.wt, new.in.acc.wt = new.in.acc.wt,
               new.out.acc.wt = new.out.acc.wt, frag.acc.wt = frag.acc.wt,
               edge.acc.wt = edge.acc.wt, edge.buf = edge.buf,
               acc.switch = acc.switch, comments = comments, 
               write.acc.db = write.acc.db, draw.maps = draw.maps, 
               pngout = pngout, test = test,  test.root = test.root, 
               user = user, password = password, 
               db.tester.name = db.tester.name, 
               alt.root = alt.root, host = host)
}
  
  

