#! /usr/bin/Rscript
##############################################################################################################
# Title      : KMLAccuracyCheck_1.3.0.R
# Purpose    : Development of QAQC accuracy assessment side of Google Earth/Maps Africa field mapping project
# Author     : Lyndon Estes
# Draws from : GMap.grid.R, GMap.server.[1|1.1].R; GMap.acc.check.1.R; GMap.QAQC.check.1.1.R
#              KMLAccuracyCheck_1.X.R
# Used by    : 
# Notes      : Notes on changes/modification moved to ChangeLog.txt (26/9/2013)
##############################################################################################################

###################
# Hardcoded values placed here for easy changing 
prjsrid       <- 97490  # EPSG identifier for equal area project
count.err.wt  <- 0.1  # Weighting given to error in number of fields identified 
in.err.wt     <- 0.7  # Weighting for in grid map discrepancy
out.err.wt    <- 0.2  # Weighting for out of grid map discrepancy
err.switch    <- 1  # Selects which area error metric used for in grid accuracy: 1 = overall accuracy; 2 = TSS
comments      <- "F"  # For testing, one can turn on print statements to see what is happening
write.err.db  <- "T"  # Option to write error metrics into error_data table in postgres (off if not "T") 
draw.maps     <- "T"  # Option to draw maps showing output error components (where maps possible, off w/o "T")
test          <- "N"  # For manual testing, one can give a single kmlid, and the code will pull the entire 
                      # assignment_data and hit_data tables to find the right assignment ids to test, "Y" for 
                      # this option, else "N" for normal production runs
test.root     <- "N"  # For testing location of working environment ("Y" or "N". "N" is for production)
###################

# Libraries
suppressMessages(library(RPostgreSQL))
suppressMessages(library(rgdal))
suppressMessages(library(rgeos))

# Run script to determine working directory and database
initial.options <- commandArgs(trailingOnly = FALSE)
arg.name <- "--file="
script.name <- sub(arg.name, "", initial.options[grep(arg.name, initial.options)])
script.dir <- dirname(script.name)
source(paste(script.dir, "getDBName.R", sep="/"))

# Paths and connections
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = db.name, user = "***REMOVED***", password = "***REMOVED***")

if(test.root == "Y") {
  prj.sql <- paste("select proj4text from spatial_ref_sys where srid=", prjsrid, sep = "")
  prjstr <- dbGetQuery(con, prj.sql)$proj4text
  print(paste("database =", db.name, "directory = ", project.root))
  print(prjstr)
  paste(project.root, "/R/Error_records/")
  print("Stopping here: Just making sure we are working and writing to the right places")
} 

if(test.root == "N") {

  # Input args
  if(test == "N") {
    args <- commandArgs(TRUE)
    mtype <- args[1]  # training "tr" or normal qaqc check "qa"
    kmlid <- args[2]  # ID of grid cell 
    assignmentid <- args[3]  # Job identifier
    if(!is.na(args[4]) & mtype == "tr") tryid <- args[4] # Try identifier (for training module only)
    if(!is.na(args[4]) & mtype == "qa") stop("QA tests do not have multiple attempts")
    if(is.na(args[4]) & mtype == "tr") stop("Training sites need to have try (attempt) specified")
    assignmentidtype <- ifelse(mtype == "tr", "training_id", "assignment_id")  # value to paste into user.sql
    if(comments == "T") print(mtype)
    if(comments == "T") print(kmlid)
    if(comments == "T") print(assignmentid)
  }
  
  #########################
  # Testing variables for remote off Africa access
  if(test == "Y") {
    hit.sql <- "select hit_id, name from hit_data"
    hits <- dbGetQuery(con, hit.sql)
    ass.sql <- "select assignment_id, hit_id, worker_id, score from assignment_data"
    asses <- dbGetQuery(con, ass.sql)
    
    # If you have the kmlid 
    if(exists("kmlid") & !exists("assignmentid")) {
      print("Using HIT ID to find assignment ID")
      hid <- hits[hits$name == kmlid, "hit_id"]
      assignmentid <- asses[asses$hit_id == hid, "assignment_id"]
      if(length(assignmentid) > 1) { 
        print("More than one assignment has been completed for this kml, selecting the first 1")
        assignmentid <- assignmentid[1]
      }
    }
    # If you have the assigment id
    if(exists("assignmentid") & !exists("kmlid")) {
      print("Using assignment ID to find HIT ID")
      hid <- asses[asses$assignment_id == assignmentid, "hit_id"]
      kmlid <- hits[hits$hit_id == hid, "name"]
    }
  }
  ########################
  # Load in necessary functions
  source(paste(script.dir, "KMLAccuracyFunctions.R", sep="/"))
  
  # Projections 
  prj.sql <- paste("select proj4text from spatial_ref_sys where srid=", prjsrid, sep = "")
  prjstr <- dbGetQuery(con, prj.sql)$proj4text
  gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"  # Always this one
  
  # Collect QAQC fields (if there are any; if not then "N" value will be returned). This should work for both
  # training and test sites
  qaqc.sql <- paste("select id,ST_AsEWKT(geom) from qaqcfields where name=", "'", kmlid, "'", sep = "")
  qaqc.geom.tab <- dbGetQuery(con, qaqc.sql)
  qaqc.hasfields <- ifelse(nrow(qaqc.geom.tab) > 0, "Y", "N") 
  if(qaqc.hasfields == "Y") {
    qaqc.geom.tab[, 2] <- gsub("^SRID=*.*;", "", qaqc.geom.tab[, 2])
    qaqc.poly.list <- createCleanTempPolyfromWKT(geom.tab = qaqc.geom.tab, crs = prjstr)
    qaqc.poly <- gUnaryUnion(qaqc.poly.list[[1]])
    qaqc.nfields <- qaqc.poly.list[[2]]
  } 
  
  # Read in user data
  if(mtype == "tr") {  # Training case
    user.sql <- paste("select name,ST_AsEWKT(geom),try from qual_user_maps where ",  assignmentidtype, "='", 
                      assignmentid, "'", " and try='",  tryid, "' order by name", sep = "")
  } else if(mtype == "qa") {  # Test case
    user.sql <- paste("select name,ST_AsEWKT(geom) from user_maps where assignment_id=", "'", 
                      assignmentid, "'", " order by name", sep = "")  
  }
  user.geom.tab <- dbGetQuery(con, user.sql)  # Collect user data and fields geometries
  user.geom.tab <- user.geom.tab[grep(kmlid, user.geom.tab$name), ]  # added to drop other training results
  user.hasfields <- ifelse(nrow(user.geom.tab) > 0, "Y", "N")  # Need to get this right
  if(user.hasfields == "Y") {  # Read in user fields if there are any
    user.geom.tab[, 2] <- gsub("^SRID=*.*;", "", user.geom.tab[, 2])
    user.poly.list <- createCleanTempPolyfromWKT(geom.tab = user.geom.tab, crs = gcs)
    user.poly <- gUnaryUnion(spTransform(user.poly.list[[1]], CRSobj = CRS(prjstr)))  # Transform to Albers
    user.nfields <- user.poly.list[[2]]  #  Record number of distinct fields observed by user
  }
  
  # Error checks begin
  #  Where no QAQC site is recorded
  # Case 1: A null qaqc site recorded as null by the observer; score set to 1
  if((qaqc.hasfields == "N") & (user.hasfields == "N")) {
    if(comments == "T") print("No QAQC or User fields")
    err <- 1
    tss.err <- 1  
    err.out <- c("total_error" = err, "count_error" = 1, "out_error" = 1, "in_error" = 1, "user_fldcount" = 0)
  } else {
    # Pick up grid cell from qaqc table, for background location, as it will be needed for the other 3 cases
    if(mtype == "tr") {  # Training case
      grid.sql <- paste("SELECT id,ST_AsEWKT(geom) from sa1kgrid where name=", "'", kmlid, "'", sep = "")
    } else if(mtype == "qa") {  # QAQC case
      grid.sql <- paste("SELECT id,ST_AsEWKT(geom) from newqaqc_sites where name=", "'", kmlid, "'", sep = "")
    }
    grid.geom.tab <- dbGetQuery(con, grid.sql)
    grid.geom.tab[, 2] <- gsub("^SRID=*.*;", "", grid.geom.tab[, 2])
    grid.poly <- createCleanTempPolyfromWKT(geom.tab = grid.geom.tab, crs = prjstr)[[1]]
  }
  
  # Case 2: A null qaqc site with fields mapped by user
  if((qaqc.hasfields == "N") & (user.hasfields == "Y")) {
    if(comments == "T") print("No QAQC fields, but there are User fields") 
    
    # Accuracy measures
    count.error <- 0  # Count accuracy is zero if QAQC has no fields but user maps even 1 field
    
    # Mapped area differences inside the target grid cell
    user.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = user.poly, byid = T)  ### Turker maps in grid
    inres <- mapError(maps = user.poly.in, truth = NULL, region = grid.poly)  # Main error metric - TSS
    
    # Secondary metric - Sensitivity of results outside of kml grid
    user.poly.out <- gDifference(spgeom1 = user.poly, spgeom2 = grid.poly, byid = T)  ### Turker maps out 
    if(is.null(user.poly.out)) {  # 16/11/12: If user finds no fields outside of box, gets credit
      out.error <- 1  
    } else {  
      out.error <- 0  # If user maps outside of box when no fields exist, sensitivity is 0
    }
    
    # Combine error metric
    err <- count.error * count.err.wt + unname(inres[[1]][err.switch]) * in.err.wt + out.error * out.err.wt 
    tss.err <- inres[[1]][2]
    err.out <- c("total_error" = err, "count_error" = count.error, "out_error" = out.error, 
                 "in_error" = unname(inres[[1]][err.switch]), "user_fldcount" = user.nfields)
  }
  
  # Cases 3 & 4
  if(qaqc.hasfields == "Y") {
    
    #  Case 3. QAQC has fields, User has no fields
    if(user.hasfields == "N") {
      if(comments == "T") print("QAQC fields but no User fields")
      # Accuracy measures
      count.error <- 0  # Count accuracy is zero if QAQC has fields but user maps none
      
      # Mapped area differences inside the target grid cell
      qaqc.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = qaqc.poly, byid = T)  # QAQC inside grid 
      qaqc.poly.out <- gDifference(spgeom1 = qaqc.poly, spgeom2 = grid.poly, byid = T)  # QAQC outside grid 
      inres <- mapError(maps = NULL, truth = qaqc.poly.in, region = grid.poly)  # Main error metric - TSS
      
      # Secondary metric - Sensitivity of results outside of kml grid
      out.error <- 0  # reduces to 0, because there is neither true positive nor false negative
      
      # Combine error metric
      err <- count.error * count.err.wt + unname(inres[[1]][err.switch]) * in.err.wt + out.error * out.err.wt 
      tss.err <- inres[[1]][2]
      err.out <- c("total_error" = err, "count_error" = count.error, "out_error" = out.error, 
                   "in_error" = unname(inres[[1]][err.switch]), "user_fldcount" = 0)
      
      # Case 4. QAQC has fields, User has fields
    } else if(user.hasfields == "Y") {
      if(comments == "T") print("QAQC fields and User fields")
      
      # Accuracy measures
      count.error <- countError(qaqc_rows = qaqc.nfields, user_rows = user.nfields)  # Count accuracy
      
      # Mapped area differences inside the target grid cell
      user.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = user.poly, byid = T) # Turker maps in grid
      qaqc.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = qaqc.poly, byid = T) # QAQC inside grid 
      user.poly.out <- gDifference(spgeom1 = user.poly, spgeom2 = grid.poly, byid = T)  # Turker maps out 
      qaqc.poly.out <- gDifference(spgeom1 = qaqc.poly, spgeom2 = grid.poly, byid = T)  # QAQC outside grid 
      inres <- mapError(maps = user.poly.in, truth = qaqc.poly.in, region = grid.poly)  # Error metric - TSS
      
      # Secondary metric - Sensitivity of results outside of kml grid
      if(is.null(user.poly.out) & is.null(qaqc.poly.out)) {
        if(comments == "T") print("No QAQC or User fields outside of grid")
        out.error <- 1  
      } else if(!is.null(user.poly.out) & !is.null(qaqc.poly.out)) {
        if(comments == "T") print("Both QAQC and User fields outside of grid")
        tpo <- gIntersection(spgeom1 = qaqc.poly.out, spgeom2 = user.poly.out)  # true positives (overlap)
        fno <- gDifference(spgeom1 = qaqc.poly.out, spgeom2 = user.poly.out)  # true positives (overlap)
        tflisto <- c("tpo", "fno")  # 29/11/12: Bug fix for crash in areas caused by null intersect
        areaso <- sapply(tflisto, function(x) ifelse(!is.null(get(x)) & is.object(get(x)), gArea(get(x)), 0))
        out.error <- areaso[1] / sum(areaso)
      } else {
        if(comments == "T") print("Either QAQC or User fields outside of grid, but not both")
        out.error <- 0
      }
      
      # Combine error metric
      err <- count.error * count.err.wt + unname(inres[[1]][err.switch]) * in.err.wt + out.error * out.err.wt 
      tss.err <- inres[[1]][2]
      err.out <- c("total_error" = err, "count_error" = count.error, "out_error" = out.error, 
                   "in_error" = unname(inres[[1]][err.switch]), "user_fldcount" = user.nfields)
    }
  } 
  
  # Insert error component statistics into the database
  if(write.err.db == "T") {
    if(mtype == "qa") {
      error.sql <- paste("insert into error_data (assignment_id, score, error1, error2, error3, error4, tss) ", 
                         "values ('", assignmentid, "', ", paste(err.out, collapse = ", "), ", ", tss.err,  
                         ")", sep = "")
    } else if(mtype == "tr") {
      error.sql <- paste("insert into qual_error_data",  
                         "(training_id, name, score, error1, error2, error3, error4, try, tss) ", 
                         "values ('", assignmentid, "', ", "'", kmlid, "', ", paste(err.out, collapse = ", "), 
                         ", ", tryid, ", ", tss.err, ")", sep = "")  # Write try error data
    }  
    ret <- dbSendQuery(con, error.sql)
  }
  
  # Pass out error metrics
  if(comments == "T") {
    cat(err.out)  # All metrics if comments are on (testing only)
  } else {
    cat(err.out[1])  # First metric if in production
  }
  
  # Map results according to error class
  if(draw.maps == "T") {
    
    if(exists("grid.poly")) bbr1 <- bbox(grid.poly)
    if(exists("qaqc.poly")) bbr2 <- bbox(qaqc.poly)
    if(exists("user.poly")) bbr3 <- bbox(user.poly)
    
    cx <- 1.5 
    lbbrls <- ls(pattern = "^bbr")
    if(length(lbbrls) > 0) {
      xr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[1, ]))
      yr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[2, ]))
      vals <- rbind(xr, yr)
      
      if(exists("grid.poly")) {
        #prj.file.path <- dbGetQuery(con, "select value from configuration where key = 'ProjectRoot'")$value
        tm <- format(Sys.time(), "%Y%m%d%H%M%OS2")  # Added 28/11/12 to time stamp output plots
        pngname <- paste(project.root, "/R/Error_records/", kmlid, "_", assignmentid, "_", tm, ".png", 
                         sep = "")
        png(pngname, height = 700, width = 700, antialias = "none")
        plot(grid.poly, xlim = vals[1, ], ylim = vals[2, ])
        objchk <- sapply(2:5, function(x) is.object(inres[[x]]))
        mpi <- names(err.out)
        plotpos <- c(0.15, 0.4, 0.65, 0.90)
        cols <- c("green4", "red4", "blue4", "grey30")
        for(i in 1:4) {
          if(objchk[i] == "TRUE") plot(inres[[i + 1]], add = T, col = cols[i])
          mtext(round(err.out[i], 3), side = 3, line = -1, adj = plotpos[i], cex = cx)
          mtext(mpi[i], side = 3, line = 0.5, adj = plotpos[i], cex = cx)
          if(exists("user.poly.out")) {
            if(!is.null(user.poly.out)) plot(user.poly.out, add = T, col = "grey")
          }
          if(exists("qaqc.poly.out")) {
            if(!is.null(qaqc.poly.out)) plot(qaqc.poly.out, add = T, col = "pink")
          }
          if(exists("tpo")) if(is.object(tpo)) plot(tpo, col = "green1", add = T)  # 29/11 added fix for nulls
          if(exists("fno")) if(is.object(tpo)) plot(fno, col = "blue1", add = T)   # 29/11 added fix for nulls
        }
        mtext(paste(kmlid, "_", assignmentid, sep = ""), side = 1, cex = cx)
        legend(x = "right", legend = c("TP", "FP", "FN", "TN"), pch = 15, bty = "n", col = cols, pt.cex = 3, 
               cex = cx)
        garbage <- dev.off()  # Suppress dev.off message
      }  
    }
  }
  
  # Clean up a bit (aids with running tests)
  rmnames <- ls()
  user.sql <- paste("select name,ST_AsEWKT(geom) from user_maps where assignment_id=", "'", 
                    assignmentid, "'", " order by name", sep = "")
  user.sql <- paste("select name,ST_AsEWKT(geom) from user_maps where assignment_id=", "'", 
                    assignmentid, "'", " order by name", sep = "")
  rm(list = rmnames[!rmnames %in% c("tab", "con")])  # remove but for var nms for test & con 
  
  # Close connection to prevent too many from being open
  garbage <- dbDisconnect(con)
}

