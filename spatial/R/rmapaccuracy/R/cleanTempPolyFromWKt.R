#' Reads in PostGIS geometry and creates a temporary shapefile out
#' @param unfixedsf sfc object for unfixed polygon
#' @param crs Coordinate reference system
#' @return A cleaned sf object
#' @details Uses callPprepair function to clean up read in polygons and write
#' @importFrom sf st_write
#' @export
cleanTempPolyFromWKT <- function(unfixedsfc, crs) {
  td <- tempdir()
  tmpnmin <- strsplit(tempfile("poly", tmpdir = ""), "/")[[1]][2]
  tmpnmout <- strsplit(tempfile("poly", tmpdir = ""), "/")[[1]][2]
  st_write(st_sf(unfixedsfc), dsn = td, layer = tmpnmin, driver = "ESRI Shapefile",update = TRUE)
  polyfixed <- callPprepair(td, spdfinname = tmpnmin, spdfoutname = tmpnmout, 
                            crs = as.character(st_crs(unfixedsfc)[1]))
  return(polyfixed)
}

