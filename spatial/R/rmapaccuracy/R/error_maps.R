#' Plotting function for KMLAccuracy
#' @param grid_poly sf polygon object of sampling grid 
#' @param qaqc_poly sf polygon object of q polygon (assuming it exists)
#' @param user_poly sf polygon object of user maps (assuming it exists)
#' @param inres Output list from mapError
#' @param err_out Vector of error terms
#' @param user_poly_out sf polygon for portion of user map outside of grid
#' @param qaqc_poly_out sf polygon for portion of q map outside of grid
#' @param tpo sf polygon of correct user maps outside of grid (if exists) 
#' @param fno sf polygon of false negative area outside of grid (if exists) 
#' @details Not currently functional, but intended to provide replacement for plotting
#' code in KMLAccuracy
#' @import sf
#' @export
error_maps <- function(grid_poly, qaqc_poly, user_poly, inres, err_out, user_poly_out, 
                       qaqc_poly_out, tpout, fnout, pngout = TRUE) {

  if(grid_poly != "null") bbr1 <- st_bbox(grid_poly)
  if(qaqc_poly != "null") bbr2 <- st_bbox(qaqc_poly)
  if(user.poly != "null") bbr3 <- st_bbox(user_poly)
  
  cx <- 1.5 
  lbbrls <- ls(pattern = "^bbr")
  if(length(lbbrls) > 0) {
    xr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[c(1,3)]))
    yr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[c(2,4)]))
    vals <- rbind(xr, yr)
    
    if(grid_poly != "null") {
      tm <- format(Sys.time(), "%Y%m%d%H%M%OS2")
      if(pngout == TRUE) {
        pngname <- paste0(dinfo["project.root"], "/spatial/R/Error_records/", 
                          kmlid, "_", assignmentid, "_", tm, ".png")
        png(pngname, height = 700, width = 700, antialias = "none")
      }
      plot(st_geometry(grid_poly), xlim = vals[1, ], ylim = vals[2, ])
      objchk <- sapply(2:5, function(x) is.object(inres[[x]]))
      mpi <- names(err_out)
      plotpos <- c(0.15, 0.4, 0.65, 0.90)
      cols <- c("green4", "red4", "blue4", "grey30")
      for(i in 1:4) {
        if(objchk[i] == "TRUE") {
          plot(st_geometry(inres[[i + 1]]), add = T, col = cols[i])
        }
        mtext(round(err_out[i], 3), side = 3, line = -1, adj = plotpos[i], 
              cex = cx)
        mtext(mpi[i], side = 3, line = 0.5, adj = plotpos[i], cex = cx)
        if(user_poly_out != "null") {
          if(length(user_poly_out) > 0) {
            plot(st_geometry(user_poly_out), add = T, col = "grey")
          }
        }
        if(qaqc.poly.out != "null") {
          if(length(qaqc_poly_out) > 0) {
            plot(st_geometry(qaqc_poly_out), add = T, col = "pink")
          }
        }
        if(tpout != "null") {
          if(is.object(tpout) & length(tpout) > 0) {
            plot(tpout, col = "green1", add = TRUE)
          }
        }
        if(exists("fno")) {
          if(is.object(fnout) & length(fnout) > 0) {
            plot(fnout, col = "blue1", add = TRUE)
          }
        }
      }
      mtext(paste0(kmlid, "_", assignmentid), side = 1, cex = cx)
      legend(x = "right", legend = c("TP", "FP", "FN", "TN"), pch = 15, 
             bty = "n", col = cols, pt.cex = 3, cex = cx)
      if(pngout == TRUE) garbage <- dev.off()  # Suppress dev.off message
    }  
  }
}
