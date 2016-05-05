#' Reads in PostGIS geometry and creates a temporary shapefile out
#' @param geom.tab Dataframe with geometry (1st col) and identifiers (2nd col)
#' @param crs Coordinate reference system
#' @return A cleaned SpatialPolygonsDataFrame
#' @details Uses callPprepair function to clean up read in polygons and write
#' @importFrom rgdal writeOGR
#' @importFrom rgeos gIsValid 
#' @export
cleanTempPolyFromWKT <- function(geom.tab, crs) {
  polyspdf <- polyFromWkt(geom.tab, crs)
  polys.count <- nrow(polyspdf)
  td <- tempdir()
  tmpnmin <- strsplit(tempfile("poly", tmpdir = ""), "/")[[1]][2]
  tmpnmout <- strsplit(tempfile("poly", tmpdir = ""), "/")[[1]][2]
  writeOGR(polyspdf, dsn = td, layer = tmpnmin, driver = "ESRI Shapefile")
  polyfixed <- callPprepair(td, spdfinname = tmpnmin, spdfoutname = tmpnmout, 
                            crs = polyspdf@proj4string)
  valid.string <- as.character(gIsValid(polyfixed))
  return(list("polygons" = polyfixed, "polygoncount" = polys.count, 
              "validity" = valid.string))
}

