#! /usr/bin/R -f
##############################################################################################################
# Title      : KMLAccuracyFunctions.R
# Purpose    : Accuracy functions used in evaluating map accuracy
# Author     : Lyndon Estes
# Draws from : KMLAccuracyCheck_1.3.0+.R
# Used by    : 
# Notes      : 
##############################################################################################################

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
