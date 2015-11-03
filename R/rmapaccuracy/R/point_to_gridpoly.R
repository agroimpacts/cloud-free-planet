#' Creates polygon grid box from point
#' @param xy A data.frame containing x and y coordinates and name of grid point
#' @param w A value in meters specifiying 1/2 the diameter of the grid polygon
#' @param CRSobj The projection string for the output polygon
#' @details This function is created for use by KMLgenerate, which uses it to 
#' convert grid points to polygons. 
#' @import sp
#' @export
point_to_gridpoly <- function(xy, w, CRSobj) {
  pols <- do.call(rbind, lapply(1:nrow(xy), function(i) {
    xs <- unlist(sapply(c(-w, w, w, -w, -w), function(x) unname(xy[i,"x"] + x)))
    ys <- unlist(sapply(c(w, w, -w, -w, w), function(x) unname(xy[i, "y"] + x)))
    p1 <- t(sapply(1:length(xs), function(i) c(xs[i], ys[i])))
    pol <- SpatialPolygons(list(Polygons(list(Polygon(p1)), i)))
    pol@proj4string <- CRSobj
    pol <- as(pol, "SpatialPolygonsDataFrame")
    pol$id <- i
    pol$name <- xy$name[i]
    pol$fwts <- xy$fwts[i]
    pol@data <- pol@data[, c("id", "name", "fwts"), drop = FALSE]
    pol
  }))
  return(pols)
}
