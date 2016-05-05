# load_f_random.R
# Recreate old Q and I site kmls

## Clear console and load required packages
rm(list=ls(all=TRUE))
library(raster)
library(rgdal)
library(rgeos)
library(gdalUtils)
library(data.table)
library(RPostgreSQL)
library(rmapaccuracy)


## Hardcoded Values 
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
alb <- paste0("+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=25 ", 
              "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")


## Determine working directory and database
dinfo <- getDBName()  # pull working environment
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")


## Get appropriate geometries from sql tables
sql <- paste0("SELECT name, ST_AsEWKT(geom) from newqaqc_sites")
q_geom <- data.table(dbGetQuery(con, sql))
sql <- paste0("SELECT name, ST_AsEWKT(geom) from qual_sites")
i_geom <- data.table(dbGetQuery(con, sql))
qi_geom <- rbind(q_geom, i_geom)


## Convert to spdf data
qisps <- sapply(1:nrow(qi_geom), function(i) { 
  qist <- unlist(strsplit(qi_geom[i, st_asewkt], ";"))
  qisp <- as(readWKT(qist[-grep("SRID", qist)], p4s = CRS(alb)), 
             "SpatialPolygonsDataFrame")
  qisp@data$name <- qi_geom[i, name]
  qisp <- qisp[, "name", drop = "FALSE"]
  qisp <- spChFIDs(qisp, as.character(qisp@data$name))
})

# Transform to geographic coordinates and write out to kmls
data_path <- path.expand(paste0(dinfo["project.root"], "/kmls_static/"))
qisps_gcs <- sapply(1:length(qisps), function(i) {
  qisp_gcs <- spTransform(x = qisps[[i]], CRSobj = CRS(gcs))
  writeOGR(qisp_gcs, dsn = paste0(data_path, qisp_gcs$name, ".kml"), 
           layer = qisp_gcs$name, driver = "KML", overwrite = TRUE)
  qisp_gcs
})
qisps_gcs <- do.call(rbind, qisps_gcs)


## Tests
library(rworldmap)
library(rworldxtra)
map <- getMap(resolution = "high")
af_cnt <- map[which(map@data$REGION == "Africa"), ]
saf <- af_cnt[af_cnt@data$SOVEREIGNT == "South Africa", ]
