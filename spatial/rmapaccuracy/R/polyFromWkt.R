#' Creates a spatialPolygonsDataFrame from a geometry table read in from Postgis
#' @param geom.tab Dataframe with geometry (1st col) and identifiers (2nd col)
#' @param crs Coordinate reference system
#' @return A SpatialPolygonsDataFrame
#' @import sp
#' @importFrom rgeos readWKT
#' @export
polyFromWkt <- function(geom.tab, crs) {
  polys <- sapply(1:nrow(geom.tab), function(x) {
    poly <- as(readWKT(geom.tab[x, 2], p4s = crs), "SpatialPolygonsDataFrame")
    poly@data$ID <- geom.tab[x, 1]
    newid <- paste(x)
    poly <- spChFIDs(poly, newid)
    return(poly)
  })
  polyspdf <- do.call(rbind, polys)
  return(polyspdf)
}

