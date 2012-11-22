#! /usr/bin/R -f
##############################################################################################################
# Title      : KMLAccuracyCheck_1.2.R
# Purpose    : Development of QAQC accuracy assessment side of Google Earth/Maps Africa field mapping project
# Author     : Lyndon Estes
# Draws from : GMap.grid.R, GMap.server.[1|1.1].R; GMap.acc.check.1.R; GMap.QAQC.check.1.1.R
#              KMLAccuracyCheck_1.X.R
# Used by    : 
# Notes      : Created 16/11/2012
#              Note on the True Skill Statistic: This can be negative, so for now I am letting it be negative,
#              and the whole error metric can be set to 0 if this is the case (occurs when user maps fields
#              but there aren't any)
#              Updating this: 
#  

##############################################################################################################
# Hardcoded values placed here for easy changing
prjsrid <- 97490  # EPSG identifier for equal area project
count.err.wt <- 0.1  # Weighting given to error in number of fields identified 
in.err.wt <- 0.7  # Weighting for in grid map discrepancy
out.err.wt <- 0.2  # Weighting for out of grid map discrepancy
err.switch <- 1  # Selects which area error metric used for in grid accuracy: 1 = overall accuracy; 2 = TSS
comments <- "T"  # For testing, one can turn on print statements to see what is happening
consel <- "africa"  # postgres connection switch: "africa" if code is run on server, "mac" for off server
test <- "Y"  # For manual testing, one can give a single kmlid, and the code will pull the entire 
             # assignment_data and hit_data tables to find the right assignment ids to test, "Y" for this
             # option, else "N" for normal production runs
write.err.log <- "T"  # Option to write text log containing error metrics (anything besides "T" turns off)
draw.maps <- "T"  # Option to draw maps showing output error components (where maps possible, off w/o "T")
##############################################################################################################

# Libraries
library(RPostgreSQL)
library(rgdal)
library(rgeos)

# Paths and connections
drv <- dbDriver("PostgreSQL")
if(consel == "africa") {
  con <- dbConnect(drv, dbname = "SouthAfrica", user = "***REMOVED***", password = "***REMOVED***")
} 
if(consel == "mac") {
  con <- dbConnect(drv, host = "africa.princeton.edu", port = 5432, dbname = "SouthAfrica", user = "***REMOVED***", 
                   password = "***REMOVED***")
}
  
# Input args
if(test == "N") {
  args <- commandArgs(TRUE)
  kmlid <- args[1]  # ID of grid cell 
  assignmentid <- args[2]  # Job identifier
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
  #userall.sql <- "select name, assignment_id, ST_AsEWKT(geom) from user_maps order by name"
  #userallmaps <- dbGetQuery(con, userall.sql)

  # If you have the kmlid
  hid <- hits[hits$name == kmlid, "hit_id"]
  assignmentid <- asses[asses$hit_id == hid, "assignment_id"]
  if(length(assignmentid) > 1) { 
    print("More than one assignment has been completed for this kml, selecting the first 1")
    assignmentid <- assignmentid[1]
  }
  # If you have the assigment id
  # assignmentid <- "2TNCNHMVHVKCPPZGWRY4M79KQKI42Q"
  # hid <- asses[ asses$assignment_id == assignmentid, "hit_id"]
  # kmlid <- hits[hits$hit_id == hid, "name"]
}
########################

# Projections 
prj.sql <- paste("select proj4text from spatial_ref_sys where srid=", prjsrid, sep = "")
prjstr <- dbGetQuery(con, prj.sql)$proj4text
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"  # Always this one

##############################################################################################################
# Functions: 
accStatsSum <- function(tp, fp, tn, fn) {
  # Calculate error statistics for two class contingency table
  agree <- tp / sum(tp, fn)  # Simple agreement class 1
  if(is.na(agree)) agree <- 0  # Set to 0 if NA
  accuracy <- sum(tp, tn) / sum(tp, tn, fp, fn)
  TSS <- agree + (tn / (fp + tn)) - 1  # Sens + specificity - 1
  #r1 <- round(accuracy * 100, 1)
  r1 <- round(accuracy, 2)
  r2 <- round(TSS, 2)
  out <- c(r1, r2)
  names(out) <- c("accuracy", "TSS")          
  return(out)
}

mapError <- function(maps, truth, region) {
# Calculates mapping accuracy for polygons relative to a "true" set of polygons
# Args: 
#   maps: The input polygons to check - can be null in case where QAQC fields exist but user maps none
#   truth: The polygons against which which accuracy will be assessed - can be NULL in case where user maps
#     exist but "truth" maps do not
#   region: A polygon defining the region in which accuracy is assessed
 
  if(is.null(truth)) {
    null <- region  # Actual null area is whole region
    tp <- 0  # True positive area is 0
    fp <- maps  # False positive area is all of maps
    fn <- 0  # No false negative area because there are no fields
    tn <- gDifference(spgeom1 = null, spgeom2 = maps, byid = F)  # false negative area (maps no, truth yes)
  } 
  if(is.null(maps)) {
    null <- gDifference(spgeom1 = region, spgeom2 = truth, byid = F)  # Actual null area in mapping region 
    tp <- 0  # No user maps, no true positive
    fp <- 0  # No user maps, no false positives
    fn <- truth  # False negative area is all of truth
    tn <- null  # True negative area is null - user gets credit for this area, even if missed fields
  }
  if(!is.null(truth) & !is.null(maps)) {
    null <- gDifference(spgeom1 = region, spgeom2 = truth, byid = F)  # Actual null area in mapping region 
    tp <- gIntersection(spgeom1 = truth, spgeom2 = maps, byid = F)  # true positives (overlap of maps & truth)
    fp <- gDifference(spgeom1 = maps, spgeom2 = truth, byid = F)  # false positive area (maps yes, truth no)
    fn <- gDifference(spgeom1 = truth, spgeom2 = maps, byid = F)  # false negative area (maps no, truth yes)
    tn <- gDifference(spgeom1 = null, spgeom2 = maps, byid = F)  # false negative area (maps no, truth yes)
  }
  areas <- sapply(list(tp, fp, tn, fn), function(x) ifelse(is.object(x), gArea(x), x))
  list(accStatsSum(areas[1], areas[2], areas[3], areas[4]), tp, fp, fn, tn)
}

createSPPolyfromWKT <- function(geom.tab, crs) {
# Function for reading in and creating SpatialPolygonsDataFrame from PostGIS
# Args: 
#   geom.tab: Dataframe with geometry and identifiers in it. Identifier must be 1st column, geometries 2nd col  
#   crs: Coordinate reference system
# Returns: 
#   A SpatialPolygonsDataFrame
  polys <- tst <- sapply(1:nrow(geom.tab), function(x) {
    poly <- as(readWKT(geom.tab[x, 2], p4s = crs), "SpatialPolygonsDataFrame")
    poly@data$ID <- geom.tab[x, 1]
    newid <- paste(x)
    poly <- spChFIDs(poly, newid)
    return(poly)
  })
  polyspdf <- do.call("rbind", polys)
}

countError <- function(qaqc, kml) {
# Calculates percent agreement between number of fields in qaqc and user kmls
# Args: 
#  qaqc: QAQC spatial object, or NULL if one doesn't exist
#  kml: User mapped fields, or NULL if they don't exist
# Returns: Score between 0-1
# Notes: Rearranges numerator and denominator of equation according to whether user mapped fields are more 
# or less than QAQC fields
  qaqc.row <- ifelse(is.null(qaqc), 0, nrow(qaqc))
  kml.row <- ifelse(is.null(kml), 0, nrow(kml))
  cden <- ifelse(qaqc.row >= kml.row, qaqc.row, kml.row)
  cnu1 <- ifelse(qaqc.row >= kml.row, qaqc.row, kml.row)
  cnu2 <- ifelse(qaqc.row >= kml.row, kml.row, qaqc.row)
  cnterr <- 1 - (cnu1 - cnu2) / cden  # Percent agreement
  return(cnterr)
}
##############################################################################################################

# First check if the QAQC site is null or not
qaqc.sql <- paste("select fields from newqaqc_sites where name=", "'", kmlid, "'", sep = "")
qaqc.hasfields <- dbGetQuery(con, qaqc.sql)$fields

# Read in user data
user.sql <- paste("select name,ST_AsEWKT(geom) from user_maps where assignment_id=", "'", 
                  assignmentid, "'", " order by name", sep = "")
user.geom.tab <- dbGetQuery(con, user.sql)  # Collect user data and fields geometries
user.hasfields <- ifelse(nrow(user.geom.tab) > 0, "Y", "N")  # Need to get this right

# Error checks begin
#  Where no QAQC site is recorded
# Case 1: A null qaqc site recorded as null by the observer; score set to 1
if((qaqc.hasfields == "N") & (user.hasfields == "N")) {
  if(comments == "T") print("No QAQC or User fields")
  err <- 1  
  err.out <- c("total_error" = err, "count_error" = 1, "out_error" = 1, "in_error" = 1)
} 

# Case 2: A null qaqc site with fields mapped by user
if((qaqc.hasfields == "N") & (user.hasfields == "Y")) {
  if(comments == "T") print("No QAQC fields, but there are User fields") 

  # Pick up grid cell from qaqc table, for background location
  grid.sql <- paste("SELECT id,ST_AsEWKT(geom) from newqaqc_sites where name=", "'", kmlid, "'", sep = "")
  grid.geom.tab <- dbGetQuery(con, grid.sql)
  grid.geom.tab[, 2] <- gsub("^SRID=*.*;", "", grid.geom.tab[, 2])
  grid.poly <- createSPPolyfromWKT(geom.tab = grid.geom.tab, crs = prjstr)
    
  # Pick up user maps
  user.geom.tab[, 2] <- gsub("^SRID=*.*;", "", user.geom.tab[, 2])
  user.poly.gcs <- createSPPolyfromWKT(geom.tab = user.geom.tab, crs = gcs)
  user.poly <- spTransform(user.poly.gcs, CRSobj = CRS(prjstr))  # Transform to Albers
  
  # Accuracy measures
  count.error <- 0  # Count accuracy is zero if QAQC has no fields but user maps even 1 field
    
  # Mapped area differences inside the target grid cell
  user.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = user.poly, byid = F)  # Turker maps in grid
  inres <- mapError(maps = user.poly.in, truth = NULL, region = grid.poly)  # Main error metric - TSS
    
  # Secondary metric - Sensitivity of results outside of kml grid
  user.poly.out <- gDifference(spgeom1 = user.poly, spgeom2 = grid.poly, byid = F)  # Turker maps out 
  if(is.null(user.poly.out)) {  # 16/11/12: If user finds no fields outside of box, gets credit
    out.error <- 1  
  } else {  
    out.error <- 0  # If user maps outside of box when no fields exist, sensitivity is 0
  }
  
  # Combine error metric
  err <- count.error * count.err.wt + unname(inres[[1]][err.switch]) * in.err.wt + out.error * out.err.wt  
  err.out <- c("total_error" = err, "count_error" = count.error, "out_error" = out.error, 
               "in_error" = unname(inres[[1]][err.switch]))
}

# Cases 3 & 4
if(qaqc.hasfields == "Y") {
  # Pick up grid cell from qaqc table, for background location
  grid.sql <- paste("SELECT id,ST_AsEWKT(geom) from newqaqc_sites where name=", "'", kmlid, "'", sep = "")
  grid.geom.tab <- dbGetQuery(con, grid.sql)
  grid.geom.tab[, 2] <- gsub("^SRID=*.*;", "", grid.geom.tab[, 2])
  grid.poly <- createSPPolyfromWKT(geom.tab = grid.geom.tab, crs = prjstr)
 
  # Pick-up QAQC poly
  qaqc.fields.sql <- paste("select id,ST_AsEWKT(geom) from qaqcfields where name=", "'", kmlid, "'", sep = "")
  qaqc.geom.tab <- dbGetQuery(con, qaqc.fields.sql)
  qaqc.geom.tab[, 2] <- gsub("^SRID=*.*;", "", qaqc.geom.tab[, 2])
  qaqc.poly <- createSPPolyfromWKT(geom.tab = qaqc.geom.tab, crs = prjstr)
  
  #  Case 3. QAQC has fields, User has no fields
  if(user.hasfields == "N") {
    if(comments == "T") print("QAQC fields but no User fields")
    # Accuracy measures
    count.error <- 0  # Count accuracy is zero if QAQC has fields but user maps none
   
    # Mapped area differences inside the target grid cell
    qaqc.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = qaqc.poly, byid = F)  # QAQC inside grid cell
    inres <- mapError(maps = NULL, truth = qaqc.poly.in, region = grid.poly)  # Main error metric - TSS
   
    # Secondary metric - Sensitivity of results outside of kml grid
    out.error <- 0  # reduces to 0, because there is neither true positive nor false negative
   
    # Combine error metric
    err <- count.error * count.err.wt + unname(inres[[1]][err.switch]) * in.err.wt + out.error * out.err.wt  
    err.out <- c("total_error" = err, "count_error" = count.error, "out_error" = out.error, 
                 "in_error" = unname(inres[[1]][err.switch]))
  
  # Case 4. QAQC has fields, User has fields
  } else if(user.hasfields == "Y") {
    if(comments == "T") print("QAQC fields and User fields")
   
    # Fetch user fields
    user.geom.tab[, 2] <- gsub("^SRID=*.*;", "", user.geom.tab[, 2])
    user.poly.gcs <- createSPPolyfromWKT(geom.tab = user.geom.tab, crs = gcs)
    user.poly <- spTransform(user.poly.gcs, CRSobj = CRS(prjstr))  # Transform to Albers
   
    # Accuracy measures
    count.error <- countError(qaqc = qaqc.poly, kml = user.poly)  # Count accuracy
   
    # Mapped area differences inside the target grid cell
    user.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = user.poly, byid = F)  # Turker maps in grid
    qaqc.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = qaqc.poly, byid = F)  # QAQC inside grid cell
    user.poly.out <- gDifference(spgeom1 = user.poly, spgeom2 = grid.poly, byid = F)  # Turker maps out 
    qaqc.poly.out <- gDifference(spgeom1 = qaqc.poly, spgeom2 = grid.poly, byid = F)  # QAQC outside grid cell
    inres <- mapError(maps = user.poly.in, truth = qaqc.poly.in, region = grid.poly)  # Error metric - TSS
   
    # Secondary metric - Sensitivity of results outside of kml grid
    if(is.null(user.poly.out) & is.null(qaqc.poly.out)) {
      if(comments == "T") print("No QAQC or User fields outside of grid")
      out.error <- 1  
    } else if(!is.null(user.poly.out) & !is.null(qaqc.poly.out)) {
      if(comments == "T") print("Both QAQC and User fields outside of grid")
      tpo <- gIntersection(spgeom1 = qaqc.poly.out, spgeom2 = user.poly.out)  # true positives (overlap)
      fno <- gDifference(spgeom1 = qaqc.poly.out, spgeom2 = user.poly.out)  # true positives (overlap)
      areaso <- sapply(list(tpo, fno), function(x) gArea(x))
      out.error <- areaso[1] / sum(areaso)
    } else {
      if(comments == "T") print("Either QAQC or User fields outside of grid, but not both")
      out.error <- 0
    }
    
    # Combine error metric
    err <- count.error * count.err.wt + unname(inres[[1]][err.switch]) * in.err.wt + out.error * out.err.wt  
    err.out <- c("total_error" = err, "count_error" = count.error, "out_error" = out.error, 
                 "in_error" = unname(inres[[1]][err.switch]))
  }
} 

# Note: I want to keep some of the additional error metrics, if possible.  I can write them from here into 
# the database, or pass them all out to python, and have the python code handle that.  
# For now, I am just passing out the primary error metric, which I am setting to zero if is is negative
#score <- ifelse(err.out[1] < 0, 0, err.out[1])
if(comments == "T") {
  cat(err.out, "\n")
} else {
  cat(err.out[1],"\n")
}



# Write error metrics to log file
if(write.err.log == "T") {
  prj.file.path <- dbGetQuery(con, "select value from configuration where key = 'ProjectRoot'")$value
  err.fname <- paste(prj.file.path, "/R/Error_records/error_metrics.Rout", sep = "")
  err.strng <- paste(kmlid, assignmentid, paste(round(err.out, 4), collapse = "  "), sep = "   ")
  if(file.exists(err.fname)) {
    write(err.strng, file = err.fname, append = T) 
  } else {
    write(err.strng, file = err.fname)
  } 
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
    
    prj.file.path <- dbGetQuery(con, "select value from configuration where key = 'ProjectRoot'")$value
    pngname <- paste(prj.file.path, "/R/Error_records/", kmlid, "_", assignmentid, ".png", sep = "")
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
      if(exists("tpo")) plot(tpo, col = "green1", add = T)
      if(exists("fno")) plot(fno, col = "blue1", add = T)
    }
    mtext(paste(kmlid, "_", assignmentid, sep = ""), side = 1, cex = cx)
    legend(x = "right", legend = c("TP", "FP", "FN", "TN"), pch = 15, bty = "n", col = cols, pt.cex = 3, 
           cex = cx)
  }  
  dev.off()
}




















