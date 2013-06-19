#! /usr/bin/R -f 
##############################################################################################################
# Title      : TKMLgenerate_1.0.R
# Purpose    : KML file generation script for training grid cells
# Author     : Lyndon Estes
# Draws from : QKMLgenerate*.R
# Used by    : 
# Notes      : Created 03/06/2013
#              Writes out manually selected grids from sa1kgrid to kmls
#              18/6/13: Re-ran because names were cleared out accidentally on this date, switching off 
#                portion to write new kml files for grid boxes
##############################################################################################################

library(RPostgreSQL)
library(rgdal)
library(rgeos)

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "SouthAfrica", user = "***REMOVED***", password = "***REMOVED***")

# Hardcoded data
country.ID <- "SA"  # Ideally this will be read out of the database, as we expand to other countries
kml.type <- "I"  # Type of KML (N for non-QAQC) (wanted to use T but there is the constraint in there)

# CRS (coordinate reference systems)
alb <- "+proj=aea +lat_1=-18 +lat_2=-32 +lat_0=0 +lon_0=24 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0"
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

# Database invariant data
kml.file.path <- dbGetQuery(con, "select value from configuration where key = 'KMLFilePath'")
kml.file.path <- kml.file.path$value
log.file.path <- dbGetQuery(con, "select value from configuration where key = 'ProjectRoot'")
log.file.path <- paste(log.file.path$value, "/log", sep="")


# # Initialize csv to log database error message
# log.hdr <- rbind("Error messages from TKMLGenerate_X.X.R", 
#                  "Time gridID afmap_errcode afmap_errmessage SouthAfrica_errcode SouthAfrica_errmessage",
#                  "#####################################################################################")
# setwd(log.file.path)
# write.table(log.hdr, file = "TKMLGenerate.log", sep = "", col.names = F, row.names = F, quote = FALSE)
# options(digit.secs = 4)  # Display milliseconds for time stamps 

# Step 1. Poll the database (newqaqc_sites) to get grid IDs where avail = F (these are the ones I manually
# set up and selected for training sites)
grids <- dbGetQuery(con, "select  id,ST_AsEWKT(geom) from sa1kgrid where avail='F'")  # 
a <- c(188774, 90531, 3470, 88962, 91222, 226678, 200999, 355992)  # order sites should be in
grids.r <- grids[match(a, grids$id), ]

#grid.IDs <- grid.IDs[, 1]

# Step 2. Draw weighted random sample = min.kml.batch
#sql <- paste("SELECT ST_AsEWKT(geom) from newqaqc_sites where id in", " (", paste(grid.IDs, collapse = ","), 
#             ")", sep = "")
# id.geom <- dbGetQuery(con, sql)  # Get the coordinates for the random grid
# geom.tab <- cbind(grid.IDs, id.geom)  # IDs and geometries in table
kmlnames <- rep(NA, nrow(grids.r))  # set up vector of kml names

# Create and print kmls
for(i in 1:nrow(grids.r)) {
    geom.str <- unlist(strsplit(grids.r[i, 2], ";"))  # Strip out polygon IDs
    geom.poly <- as(readWKT(geom.str[-grep("SRID", geom.str)], p4s = alb), "SpatialPolygonsDataFrame") #SPDF
    colnames(geom.poly@data)[1] <- "ID"  # Rename ID field
    
    # Step 3. Create a file name for the kml
	  geom.poly@data$ID <- grids.r[i, 1]
    geom.poly@data$kmlname <- paste(country.ID, geom.poly@data$ID, sep = "")
    kmlnames[i] <- geom.poly@data$kmlname 
    
    # Step 4. Write out the kml
    geom.poly.gcs <- spTransform(x = geom.poly, CRSobj = CRS(gcs))  # First convert to geographic coords
    setwd(kml.file.path)  # Change into kml directory
#     writeOGR(geom.poly.gcs, dsn = paste(geom.poly.gcs@data$kmlname, "kml", sep = "."), 
#              layer = geom.poly.gcs@data$kmlname, driver = "KML", dataset_options = c("NameField = name"), 
#              overwrite = T)  # Write it
    print(paste("kml for", geom.poly.gcs@data$kmlname, "written"))
}
        
# Update afmap with filename and kml_type
ret <- dbSendQuery(con, paste("insert into kml_data (name, kml_type) values ", 
                              paste("('", kmlnames, "', ", "'", kml.type, "')", sep = "", collapse = ","), 
                              sep = ""))
# Update SouthAfrica to show grid is no longer available for selecting/writing
#ret2 <- dbSendQuery(con2, paste("UPDATE newqaqc_sites SET avail='F' where id in", 
#                                "(", paste(geom.tab[, 1], collapse = ","), ")", sep = ""))
    
# Database error handling
# exception <- dbGetException(con)  # South Africa update exceptions
# if (exception$errorNum != 0) {
#   print("Error updating either afmap or SouthAfrica")
#   errors <- paste(gsub("EDT", "", Sys.time()), "  ", id.rand, "  ", paste(exception, collapse = "    "), 
#                   "  ", paste(exception2, collapse = "    "))
#   write(errors, file = "RKMLGenerate.log", append = T)
#   quit(status=exception$errorNum, save="no")
# }
