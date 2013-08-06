#! /usr/bin/R -f
##############################################################################################################
# Title      : KMLAccuracyCheck_1.3.0.R
# Purpose    : Development of QAQC accuracy assessment side of Google Earth/Maps Africa field mapping project
# Author     : Lyndon Estes
# Draws from : GMap.grid.R, GMap.server.[1|1.1].R; GMap.acc.check.1.R; GMap.QAQC.check.1.1.R
#              KMLAccuracyCheck_1.X.R
# Used by    : 
# Notes      : Created 19/11/2012 (version 1.2.1)
#              Note on the True Skill Statistic: This has been replaced by the overall accuracy score from 
#              Version *1.2.X.R onwards because it is more forgiving and gives more credit for TRUE negative
#              errors. 
#              Changes: 
#                 * Installed numerous testing switches and routines (retrieve assignment id, test from 
#                   mac off-server, write accuracy measures to text file, map error components)
#                 * Projected coordinate system now read in EPSG id from ***REMOVED*** database
#                 * Counting user fields as error component
#                 * Mapping accuracy in grid box now assessed with overall accuracy, but switch allows TSS
#                   to be used 
#                 * Checking input polygons (qaqc and user) for overlaps, and unioning any that are found
#                 * Reduced code lines by moving up polygon read in functions to beginning of section 
#                   codes. Introduced polygons cleaning function here, and created two new variables to 
#                   record number of rows in user and qaqc fields before unioning (user_nfields, qaqc_nfields)
#                     ** Changed countError function to take vectors rather than spatial objects to deal with
#                        this change
#                  20/11/12:
#                  * Fixed missing user_nfields in err.out vectors for Cases 2-4
#                  * Removed line feeds in cat commands, suppressed dev.off() messages
#                  28/11/12: Version update to 1.2.2. Changes tested in 1.2.1.test.R in /Test_and_Old_R 
#                    to prevent conflict with active use of system
#                    Fixes:
#                    * Fixed bug throwing null results in mapError: set null tp,fp,fn,tn values to 0 before 
#                      passing to function calling gArea: fixes lines 155-156
#                    * Fixed incorrect accuracy statistic as found with assignment id 
#                      286PLSP75KLMCLHI0Z8QHQVJRSKZTB. Result too generous. Fix by making sure correct names
#                      are being referenced in call to accStatsSum. Lines 157-178
#                    Additions:
#                    * Added time stamp to output plots so that multiple results of assignment can be kept
#                      Lines 386-388
#                    * Added statements to pass error components to error_data table: Lines 346-349
#                    * Conditional statements put into lines 94-109 to allow testing with either kmlid or 
#                      assignmentid entered singly
#                  29/11/12: 
#                    Fixes
#                    * Intersection bug caused in case 3 with fields intersection issues. Updated all by 
#                      setting all gIntersection and gDifference operations to byid = T
#                    * Plotting option did not draw portion of QAQC outside of grid. Added qaqc.poly.out
#                      routine to case use (line 306)
#                    * After first fix, still found error caused in case 4 with geometries being contained by
#                      other geometries at qaqc.poly.out call under case 4. Fixed by turning off function
#                      cleanPolyByUnion and replacing with straight gUnaryUnion function. Seems to work
#                    * Error thrown by null tpo/tno error under case 4 where both user and qaqc fields outside
#                      of grid didn't intersect: transported in same fix from mapError function
#                    * Bug for plotting function caused by null tpo/fno results also fixed by adding check for
#                      is.object to conditional statement
#                    Additions
#                    * Added conditional statement and switch to toggle writing to error_data on and off
#                  5/4/2013: 
#                    Beginning point for code version update to KMLAccuracyCheck.1.2.3.R
#                    Fixes: 
#                    * Major modification: Polygon cleaning installed via pprepair to fix unclean topologies
#                      This means that user and qaqc polygons are read in, polygon numbers counted, written to
#                      temporary ESRI shapefiles, cleaned via pprepair to new temporary shapefiles, then read
#                      back in for error checking operations. This is achieved via two new functions: 
#                      ** callPprepair, which is used by createCleanTempPolyfromWKT
#                      ** These replace cleanPolyByUnions and createPolyfromWKT
#                    * gUnaryUnion is still performed on the cleaned polygon sets to facilitate easier merges
#                      and intersects
#                   19/4/2013: 
#                     Note: Bug remains in pprepair on one set of polygons that starts an infinite loop
#                   13/6/2013: 
#                     Update to version 1.2.4.
#                     * Change to take argument from Turker training sites as well normal assignments
#                       ** Uses this format suggested by Dennis, with modifications
#                          KMLAccuracyCheck.R ["tr"|"qa"] <kmlName> <trainingId|assignmentId>
#                          where "tr" is for training sites, and "qa" for qaqc sites
#                     * Deleted commented out functions that persisted in version 1.2.3.
#                   14/6/2013: 
#                     * Edited feature to write error components to database, reflecting new database added for
#                     for qual_error_data.
#                     * Removed code to write to text error log, now redundant
#                   19/6/2013: 
#                      ********** Update to version 1.3.0 ************
#                     * Editing to incorporate new changes to training module, where new database allows 
#                       multiple user maps per training site
#                     * Error algorithm switched to TSS (err.switch = 2)
#                     * Wrote in logic to check if training error map was recorded more than once. If so, add
#                       10 to try attempt number and write again
#                       [switched this option off]
#                     * Simplified logic for reading in qaqc maps. Removed check to newqaqc_sites for whether
#                       fields exist or not, which might make this table redundant. 
#                     * Compare to version 1.2.4 in Test_and_Old_R or in SVN to recover changes
#                   20/6/2013: Returned error switch to original accuracy measure, as TSS is too strict
#                   6/8/2013: Made modification to write TSS to *error_data tables
#                    
##############################################################################################################
# Hardcoded values placed here for easy changing 
prjsrid       <- 97490  # EPSG identifier for equal area project
count.err.wt  <- 0.1  # Weighting given to error in number of fields identified 
in.err.wt     <- 0.7  # Weighting for in grid map discrepancy
out.err.wt    <- 0.2  # Weighting for out of grid map discrepancy
err.switch    <- 1  # Selects which area error metric used for in grid accuracy: 1 = overall accuracy; 2 = TSS
comments      <- "F"  # For testing, one can turn on print statements to see what is happening
consel        <- "africa"  # postgres connection switch: "africa" when run on server, "mac" for off server
write.err.db  <- "T"  # Option to write error metrics into error_data table in postgres (off if not "T") 
draw.maps     <- "T"  # Option to draw maps showing output error components (where maps possible, off w/o "T")
test          <- "N"  # For manual testing, one can give a single kmlid, and the code will pull the entire 
                      # assignment_data and hit_data tables to find the right assignment ids to test, "Y" for 
                      # this option, else "N" for normal production runs
##############################################################################################################

# Libraries
suppressMessages(library(RPostgreSQL))
suppressMessages(library(rgdal))
suppressMessages(library(rgeos))

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
    null <- gDifference(spgeom1 = region, spgeom2 = truth, byid = T)  # Actual null area in mapping region 
    tp <- gIntersection(spgeom1 = truth, spgeom2 = maps, byid = T)  # true positives (overlap of maps & truth)
    fp <- gDifference(spgeom1 = maps, spgeom2 = truth, byid = T)  # false positive area (maps yes, truth no)
    fn <- gDifference(spgeom1 = truth, spgeom2 = maps, byid = T)  # false negative area (maps no, truth yes)
    tn <- gDifference(spgeom1 = null, spgeom2 = maps, byid = T)  # false negative area (maps no, truth yes)
  }
  tflist <- c("tp", "fp", "fn", "tn")  # 28/11/12: Bug fix for crash in areas caused by null fp results
  areas <- sapply(tflist, function(x) ifelse(!is.null(get(x)) & is.object(get(x)), gArea(get(x)), 0))
  names(areas) <- tflist  # Added 28/11/12 to have specific names from areas to pass to accStatsSum
  list(accStatsSum(tp = areas["tp"], fp = areas["fp"], fn = areas["fn"], tn = areas["tn"]), tp, fp, fn, tn)  
}

countError <- function(qaqc_rows, user_rows) {
# Calculates percent agreement between number of fields in qaqc and user kmls
# Args: 
#  qaqc_rows: vector containing number of QAQC rows, or NULL if one doesn't exist
#  kml: User mapped fields, or NULL if they don't exist
# Returns: Score between 0-1
# Notes: Rearranges numerator and denominator of equation according to whether user mapped fields are more 
# or less than QAQC fields
  cden <- ifelse(qaqc_rows >= user_rows, qaqc_rows, user_rows)
  cnu1 <- ifelse(qaqc_rows >= user_rows, qaqc_rows, user_rows)
  cnu2 <- ifelse(qaqc_rows >= user_rows, user_rows, qaqc_rows)
  cnterr <- 1 - (cnu1 - cnu2) / cden  # Percent agreement
  return(cnterr)
}

callPprepair <- function(dirnm, spdfinname, spdfoutname, crs = crs) {
# Function to make system call to polygon cleaning program pprepair
# Args: 
#   dirnm: directory where the shapefiles will go
#   spdfinname: Name of the ESRI shapefile written to disk that needs cleaning, without the .shp extension
#   spdfoutname: Name of shapefile that pprepair should write to, without the .shp extension
# Returns: 
#   spdf of cleaned polygons, pointing to a temporary shapefile written to disk
  
  inname <- paste(dirnm, "/", spdfinname, ".shp", sep = "")
  outname <- paste(dirnm, "/", spdfoutname, ".shp", sep = "")
  ppcall <- paste("/usr/local/bin/pprepair -i", inname, "-o", outname, "-fix")
  ctch <- system(ppcall, intern = TRUE)
  polyfixed <- readOGR(dsn = dirnm, layer = spdfoutname, verbose = FALSE)
  polyfixed@proj4string <- crs
  return(polyfixed)
}

createCleanTempPolyfromWKT <- function(geom.tab, crs) {
# Function for reading in a spatial geometry from PostGIS and creating a temporary shapefile out of it  
# Args: 
#   geom.tab: Dataframe with geometry and identifiers in it. Identifier must be 1st column, geometries 2nd col  
#   crs: Coordinate reference system
# Returns: 
#   A SpatialPolygonsDataFrame
# Notes: 
#   Uses callPprepair function to clean up read in polygons and write them to a temporary location
  polys <- tst <- sapply(1:nrow(geom.tab), function(x) {
    poly <- as(readWKT(geom.tab[x, 2], p4s = crs), "SpatialPolygonsDataFrame")
    poly@data$ID <- geom.tab[x, 1]
    newid <- paste(x)
    poly <- spChFIDs(poly, newid)
    return(poly)
  })
  polyspdf <- do.call("rbind", polys)
  polys.count <- nrow(polyspdf)
  td <- tempdir()
  tmpnmin <- strsplit(tempfile("poly", tmpdir = ""), "/")[[1]][2]
  tmpnmout <- strsplit(tempfile("poly", tmpdir = ""), "/")[[1]][2]
  writeOGR(polyspdf, dsn = td, layer = tmpnmin, driver = "ESRI Shapefile")
  polyfixed <- callPprepair(td, spdfinname = tmpnmin, spdfoutname = tmpnmout, crs = polyspdf@proj4string)
  valid.string <- as.character(gIsValid(polyfixed))
  return(list("polygons" = polyfixed, "polygoncount" = polys.count, "validity" = valid.string))
}

##############################################################################################################

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
  # Pick up grid cell from qaqc table, for background location, as it will be needed for the other three cases
  if(mtype == "tr") {  # Training case
    grid.sql <- paste("SELECT id,ST_AsEWKT(geom) from sa1kgrid where name=", "'", kmlid, "'", sep = "")
  } else if(mtype == "tr") {  # QAQC case
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
    qaqc.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = qaqc.poly, byid = T)  # QAQC inside grid cell
    qaqc.poly.out <- gDifference(spgeom1 = qaqc.poly, spgeom2 = grid.poly, byid = T)  # QAQC outside grid cell
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
    qaqc.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = qaqc.poly, byid = T) # QAQC inside grid cell
    user.poly.out <- gDifference(spgeom1 = user.poly, spgeom2 = grid.poly, byid = T)  # Turker maps out 
    qaqc.poly.out <- gDifference(spgeom1 = qaqc.poly, spgeom2 = grid.poly, byid = T)  # QAQC outside grid cell
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
#     error.sql <- paste("insert into error_data (assignment_id, score, error1, error2, error3, error4) ", 
#                        "values ('", assignmentid, "', ", paste(err.out, collapse = ", "), ")", sep = "")
    error.sql <- paste("insert into error_data (assignment_id, score, error1, error2, error3, error4, tss) ", 
                       "values ('", assignmentid, "', ", paste(err.out, collapse = ", "), ", ", tss.err,  
                       ")", sep = "")
  } else if(mtype == "tr") {
    error.sql <- paste("insert into qual_error_data",  
                       "(training_id, name, score, error1, error2, error3, error4, try, tss) ", 
                       "values ('", assignmentid, "', ", "'", kmlid, "', ", paste(err.out, collapse = ", "), 
                       #", ", tryid2, ")", sep = "")  # Write try error data
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
      prj.file.path <- dbGetQuery(con, "select value from configuration where key = 'ProjectRoot'")$value
      tm <- format(Sys.time(), "%Y%m%d%H%M%OS2")  # Added 28/11/12 to time stamp output plots
      pngname <- paste(prj.file.path, "/R/Error_records/", kmlid, "_", assignmentid, "_", tm, ".png", 
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


