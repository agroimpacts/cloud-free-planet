#' Create a dummy raster that matches the dimensions of master grid
#' @param xmin Minimum X coordinate, defaulted to -17.541 of Africa grid
#' @param xmax Maximum X coordinate, defaulted to 51.419 of Africa grid
#' @param ymin Minimum Y coordinate, defaulted to -34.845 of Africa grid
#' @param ymax Maximum Y coordinate, defaulted to 37.540 of Africa grid
#' @param res Resolution of grid, default 0.005
#' @details Set up dummy raster. Assumes EPSG 4326. 
#' @return Unpopulated raster set to provided extent and resolution
#' @importFrom raster raster extent
#' @keywords internal
dummy_raster <- function(xmin = -17.541, xmax = 51.419, ymin = -34.845, 
                         ymax = 37.540, res = 0.005) {
  r <- raster(extent(c(xmin, xmax, ymin, ymax)), res = res)
  return(r)
}

#' Retrieve raster row and column numbers for x, y coordinate and raster
#' @param x Vector of x coordinates
#' @param y Vector of y coordinates
#' @param r Reference raster
#' @param offset Adjust to match referencing convention, e.g. 0-based (-1)
#' @details Used to find row and cell number for a given raster.
#' @return Matrix of row and column number
#' @importFrom raster rowFromY colFromX
#' @keywords export
#' @examples 
#' library(rmapaccuracy)
#' r <- dummy_rast()
#' rowcol_from_xy(r, x = 8.9065, y = 37.5375)
# coninfo <- mapper_connect(user = pgupw$user, password = pgupw$password,
#                           db.tester.name = "lestes", 
#                           host = "crowdmapper.org")
# xy_tabs <- coninfo$con %>% tbl("master_grid") %>%
#   filter((gid >= 1) & (gid <= 20)) %>%
#   select(id, name, x, y) %>%
#   head(20) %>% collect()
# xy_tabs <- data.table(xy_tabs)  # convert to data.table (not needed???)
rowcol_from_xy <- function(x, y, r, offset = -1) {
  rcmat <- cbind(x = colFromX(r, x) + offset, y = rowFromY(r, y) + offset)
  return(rcmat)
}
