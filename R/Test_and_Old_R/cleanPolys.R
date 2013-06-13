# cleanPolys.R
# Functions for reading in cleaned polygons via pprepair


callPprepair <- function(dirnm, spdfinname, spdfoutname, crs = crs) {
  # Function to make system call to polygon cleaning program pprepair
  # Args: 
  #   dirnm: directory where the shapefiles will go
  #   spdfinname: Name of the ESRI shapefile written to disk that needs cleaning, without the .shp extension
  #   spdfoutname: Name of shapefile that pprepair should write to, without the .shp extension
  # Returns: 
  #   spdf of cleaned polygons, pointing to a temporary shapefile written to disk
  
  #crs = prjstr
  #dirnm = td; spdfinname = tmpnmin; spdfoutname = tmpnmout
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
  #td <- "/var/www/html/afmap/R/tmp/"
  td <- tempdir()
  tmpnmin <- strsplit(tempfile("poly", tmpdir = ""), "/")[[1]][2]
  tmpnmout <- strsplit(tempfile("poly", tmpdir = ""), "/")[[1]][2]
  writeOGR(polyspdf, dsn = td, layer = tmpnmin, driver = "ESRI Shapefile")
  polyfixed <- callPprepair(td, spdfinname = tmpnmin, spdfoutname = tmpnmout, crs = polyspdf@proj4string)
  valid.string <- as.character(gIsValid(polyfixed))
  return(list("polygons" = polyfixed, "polygoncount" = polys.count, "validity" = valid.string))
}