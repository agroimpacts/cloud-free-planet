#' Function to make system call to polygon cleaning program pprepair
#' @param dirnm directory where the shapefiles will go
#' @param spdfinname Name of ESRI shapefile that needs cleaning (no .shp ext)
#' @param spdfoutname: Name of pprepair output shapefile (no .shp ext)
#' @return polyfixed of cleaned polygons, read in from temporary .shp written to disk
#' @importFrom sf st_read
#' @export 
callPprepair <- function(dirnm, spdfinname, spdfoutname, crs = crs) {
  inname <- paste0(dirnm, "/", spdfinname, ".shp")
  outname <- paste0(dirnm, "/", spdfoutname, ".shp")
  proot <- getDBName()
  ppcall <- paste0(proot["project.root"], "/pprepair/pprepair -i ", inname,
                   " -o ", outname, " -fix")
  # ppcall <- paste0("/home/sye/github/pprepair/pprepair/build/pprepair -i ", inname, 
  #                                " -o ", outname, " -fix") #test code
  ctch <- system(ppcall, intern = TRUE)
  polyfixed <- st_read(dsn = dirnm, layer = spdfoutname)
  st_crs(polsf) <- crs
  return(polyfixed)
}

