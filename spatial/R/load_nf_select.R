# load_nf_select.R
# Create and load n and f sites from Zambia and Tanzania

## Clear console and load required packages
rm(list=ls(all=TRUE))
library(raster)
# library(rgdal)
# library(rgeos)
# library(gdalUtils)
library(data.table)
# library(RPostgreSQL)
library(rmapaccuracy)
library(sp)


## Set working directory
dinfo <- getDBName()  # pull working environment
b_path <- paste0(dinfo["project.root"], "/spatial/data")
setwd(b_path)

## Set hardcoded Values 
diam <- 500
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
alb <- paste0("+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=25 ", 
              "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")

## Connect to database
dinfo <- getDBName()  # pull working environment
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")

# Get a list of all proj4 strings by zone
sql <- paste0("select proj4text from spatial_ref_sys where auth_name='map_af' ",
              "order by auth_srid")
prjstr <- dbGetQuery(con, sql)$proj4text


## Import data
# Zambia data
# The following are ground-mapped field boundaries (for F site selection)
dir_path <- paste0(b_path, "/zambia/SP_field_boundaries/")
flds_olzm <- readOGR(dsn = paste0(dir_path, "SP_FieldBoundaries_UTM35S_WGS84.shp"), 
                     layer = "SP_FieldBoundaries_UTM35S_WGS84")
dir_path <- paste0(getwd(), "/zambia/SP_field_boundaries_new/")
flds_nwzm <- readOGR(dsn = paste0(dir_path, "fldbnds.316.cleaned.shp"), 
                   layer = "fldbnds.316.cleaned")
dir_path <- paste0(getwd(), "/zambia/EP_field_boundaries/")
flds_epzm <- readOGR(dsn = paste0(dir_path, "EP_FieldBoundaries_UTM36S_WGS84.shp"), 
                     layer = "EP_FieldBoundaries_UTM36S_WGS84")
dir_path <- paste0(getwd(), "/zambia/SP/")
# The following define the boundaries for deliberately selected N sites
sea_spzm <- readOGR(dsn = paste0(dir_path, "Southern_seas.shp"), 
                    layer = "Southern_seas")
proj4string(sea_spzm) <- gcs
hhpnts <- read.csv(paste0(getwd(), "/zambia/p_for_f_sites-2.csv"), 
                   header = TRUE, sep = ",")  # household points

# Tanzania data (F sites only)
dir_path <- paste0(getwd(), "/tanzania/field-boundaries/")
flds_gotz <- readOGR(dsn = paste0(dir_path, "L2KilS1Gon_AMU-Boundaries.shp"), 
                     layer = "L2KilS1Gon_AMU-Boundaries")
flds_mbtz <- readOGR(dsn = paste0(dir_path, "L2KilS2Mbu_AMU-Boundaries.shp"), 
                     layer = "L2KilS2Mbu_AMU-Boundaries")
flds_iktz <- readOGR(dsn = paste0(dir_path, "L3NjoS1Iki_AMU-Boundaries.shp"), 
                     layer = "L3NjoS1Iki_AMU-Boundaries")
flds_iwtz <- readOGR(dsn = paste0(dir_path, "L3NjoS2Iwu_AMU-Boundaries.shp"), 
                     layer = "L3NjoS2Iwu_AMU-Boundaries")


## Reformat data
# Drop attributes except for numerical ID
flds_olzm <- flds_olzm[, "FIELD_ID", drop = "FALSE"]
colnames(flds_olzm@data) <- "Id"
flds_nwzm <- flds_nwzm[, "UID", drop = "FALSE"]
colnames(flds_nwzm@data) <- "Id"
flds_epzm <- flds_epzm[, "Field_ID", drop = "FALSE"]
colnames(flds_epzm@data) <- "Id"
sea_spzm <- sea_spzm[, "OBJECTID", drop = "FALSE"]
colnames(sea_spzm@data) <- "Id"

# Rename ID slots
flds_olzm@data$Id <- as.character(paste0("OLZM", seq(1, length(flds_olzm))))
flds_olzm <- spChFIDs(flds_olzm, flds_olzm@data$Id)
flds_nwzm@data$Id <- as.character(paste0("NWZM", seq(1, length(flds_nwzm))))
flds_nwzm <- spChFIDs(flds_nwzm, flds_nwzm@data$Id)
flds_epzm@data$Id <- as.character(paste0("EPZM", seq(1, length(flds_epzm))))
flds_epzm <- spChFIDs(flds_epzm, flds_epzm@data$Id)
flds_gotz@data$Id <- as.character(paste0("GOTZ", seq(1, length(flds_gotz))))
flds_gotz <- spChFIDs(flds_gotz, flds_gotz@data$Id)
flds_mbtz@data$Id <- as.character(paste0("MBTZ", seq(1, length(flds_mbtz))))
flds_mbtz <- spChFIDs(flds_mbtz, flds_mbtz@data$Id)
flds_iktz@data$Id <- as.character(paste0("IKTZ", seq(1, length(flds_iktz))))
flds_iktz <- spChFIDs(flds_iktz, flds_iktz@data$Id)
flds_iwtz@data$Id <- as.character(paste0("IWTZ", seq(1, length(flds_iwtz))))
flds_iwtz <- spChFIDs(flds_iwtz, flds_iwtz@data$Id)
sea_spzm@data$Id <- as.character(paste0("SEZM", seq(1, length(sea_spzm))))
sea_spzm <- spChFIDs(sea_spzm, sea_spzm@data$Id)

# Transform to Albers Africa
flds_olzm_alb <- spTransform(flds_olzm, CRS(alb))
flds_nwzm_alb <- spTransform(flds_nwzm, CRS(alb))
flds_epzm_alb <- spTransform(flds_epzm, CRS(alb))
flds_gotz_alb <- spTransform(flds_gotz, CRS(alb))
flds_mbtz_alb <- spTransform(flds_mbtz, CRS(alb))
flds_iktz_alb <- spTransform(flds_iktz, CRS(alb))
flds_iwtz_alb <- spTransform(flds_iwtz, CRS(alb))
sea_spzm_alb <- spTransform(sea_spzm, CRS(alb)) 

# Combine Tanzania and Zambia sites
# F select sites
flds_tzzm_alb <- rbind(flds_olzm_alb, flds_nwzm_alb, flds_epzm_alb, flds_gotz_alb, 
                       flds_mbtz_alb, flds_iktz_alb, flds_iwtz_alb)
# N select sites
flds_spzm_alb <- rbind(flds_olzm_alb, flds_nwzm_alb)

## Create boundary shapes
# Create shape for field boundaries
u <- 10
fdims <- extent(flds_spzm_alb)[c(1, 2, 3, 4)]
fl <- list(floor, ceiling, floor, ceiling)
fdims2 <- sapply(1:4, function(x) fl[[x]](fdims[x]*u)/u)
fmat <- rbind(c(fdims2[1], fdims2[3]), c(fdims2[1], fdims2[4]), 
              c(fdims2[2], fdims2[4]), c(fdims2[2], fdims2[3]))
fbnds_spzm_alb <- SpatialPolygons(list(Polygons(list(Polygon(fmat)), 1)))
crs(fbnds_spzm_alb) <- alb

# Convert shape for hh boundaries
u <- 10
hhdims <- c(min(hhpnts$Long, na.rm = T), max(hhpnts$Long, na.rm = T), 
            min(hhpnts$Lat, na.rm = T), max(hhpnts$Lat, na.rm = T))
fl <- list(floor, ceiling, floor, ceiling)
hhdims2 <- sapply(1:4, function(x) fl[[x]](hhdims[x]*u)/u)
hhmat <- rbind(c(hhdims2[1], hhdims2[3]), c(hhdims2[1], hhdims2[4]), 
               c(hhdims2[2], hhdims2[4]), c(hhdims2[2], hhdims2[3]))
hh_spzm <- SpatialPolygons(list(Polygons(list(Polygon(hhmat)), 1)))
crs(hh_spzm) <- gcs
hh_spzm_alb <- spTransform(hh_spzm, CRS(alb))


## Find intersecting cell ids
# Check intersections
test <- gContains(fbnds_spzm_alb, hh_spzm_alb)
# Because the boundary of the fields contains the entirity of the household 
# points, I only use the field boundaries for the following intersection

# Find intersecting area
index <- gIntersects(fbnds_spzm_alb, sea_spzm_alb, byid = TRUE)
int_spzm_alb <- sea_spzm_alb[which(index[index=TRUE]), ]
# plot(int_spzm_alb)

# Crop and find ids of intersection cells 
afgridr <- brick(paste0(getwd(), "/shapes/africa_master_brick.tif"))[[1]]
crop_spzm <- crop(afgridr, extent(int_spzm_alb), snap = "out")
crop_tzzm <- crop(afgridr, extent(flds_tzzm_alb), snap = "out")
ids_spzm <- sort(unique(unlist(extract(crop_spzm, int_spzm_alb, small = TRUE))))
ids_tzzm <- sort(unique(unlist(extract(crop_tzzm, flds_tzzm_alb, 
                                       small = TRUE))))
ids_all <- unique(c(ids_spzm, ids_tzzm))

# checks
# r <- Which(crop_spzm %in% ids_spzm)
# r[r == 0] <- NA
# plot(int_spzm_alb)
# points(rasterToPoints(r), cex = 0.1, pch = 20, col = "red")
# plot(rasterToPoints(r), pch = 20, cex = 0.1)
# r <- Which(crop_tzzm %in% ids_tzzm)
# r[r == 0] <- NA
# plot(flds_tzzm_alb)
# points(rasterToPoints(r), cex = 0.1, pch = 20, col = "red")

# Create table of mastergrid entries
mgrid <- fread(paste0(getwd(),"/gridfiles/africa_master_grid.csv"))
xy_spzm <- copy(mgrid[ID %in% ids_spzm, ])
xy_tzzm <- copy(mgrid[ID %in% ids_tzzm, ])

# first remove n_select sites that are common to f_select, followed by 
# removal of any names in Q sites
xy_spzm <- xy_spzm[which(!xy_spzm$name %in% xy_tzzm$name), ]  # f_select
qnms <- dbGetQuery(con, "SELECT name FROM kml_data")$name
xy_spzm <- xy_spzm[which(!xy_spzm$name %in% qnms), ]  # Q sites

ids_all <- unique(c(xy_spzm$ID, xy_tzzm$ID))

# now combine and shuffle row order
xy_all <- copy(mgrid[ID %in% ids_all, ])
set.seed(234)
xy_spzm <- xy_spzm[sample(nrow(xy_spzm)), ] # shuffle row order
set.seed(234)
xy_tzzm <- xy_tzzm[sample(nrow(xy_tzzm)), ] # shuffle row order
set.seed(234)
xy_all <- xy_all[sample(nrow(xy_all)), ] # shuffle row order

## Process points into kmls
# Convert point data to proper projections
gpnts_all <- sapply(1:nrow(xy_all), function(i) { 
  zn <- xy_all[i, zone]
  xy <- data.frame(xy_all[i, ])
  coordinates(xy) <- xy[2:3]
  xy <- xy[, 4:6]
  crs(xy) <- alb
  xy_trans <- spTransform(xy, CRS(prjstr[zn]))
})

# Convert points to polygons
gpols_all <- sapply(1:nrow(xy_all), function(i) { 
  xy_trans <- gpnts_all[[i]] 
  proj4 <- proj4string(xy_trans)
  ptdata <- data.frame(xy_trans)
  gpol <- point_to_gridpoly(xy = ptdata, w = diam, CRSobj = CRS(proj4))
  gpol@data$zone <- xy_trans@data$zone
  gpol@data$id <- i
  gpol <- spChFIDs(gpol, as.character(gpol@data$id))
})

# Transform to geographic coordinates and write out to kmls
data_path <- path.expand(paste0(dinfo["project.root"], "/kmls/"))
gpols_all_gcs <- sapply(1:length(gpols_all), function(i) {
  gpol_gcs <- spTransform(x = gpols_all[[i]], CRSobj = CRS(gcs))
  writeOGR(gpol_gcs, dsn = paste0(data_path, gpol_gcs$name, ".kml"), 
           layer = gpol_gcs$name, driver = "KML", overwrite = TRUE)
  gpol_gcs
})
gpols_all_gcs <- do.call(rbind, gpols_all_gcs)

## Update databases
# Check if table exists for selected Zambia sites, create if doesn't exist
# dbRemoveTable(con, "n_select")
if(!dbExistsTable(con, "n_select")) {
  sql <- paste("CREATE TABLE n_select",
               "(gid integer PRIMARY KEY,",
               "id integer, x double precision,",
               "y double precision, name varchar,",
               "fwts integer, zone integer)")
  dbSendQuery(con, sql)
}

# Upload n_select data
sqlv <-  paste0("('", seq(1, length(ids_spzm)), "','", xy_spzm$ID, "','", 
                xy_spzm$x, "','", xy_spzm$y,"','", xy_spzm$name,"','", 
                xy_spzm$fwts,"','", xy_spzm$zone,"')", collapse = ",")
sql <- paste0("insert into n_select (gid, id, x, y, name, fwts, zone) 
             values ", sqlv)
dbSendQuery(con, sql)
dbSendQuery(con, "VACUUM ANALYZE n_select")

# check for f_select table, create if doesn't exist
# dbRemoveTable(con, "f_select")
if(!dbExistsTable(con, "f_select")) {
  sql <- paste("CREATE TABLE f_select",
               "(gid integer PRIMARY KEY,",
               "id integer, x double precision,",
               "y double precision, name varchar,",
               "fwts integer, zone integer)")
  dbSendQuery(con, sql)
}

# Upload f_select data
sqlv <-  paste0("('", seq(1,length(ids_tzzm)), "','", xy_tzzm$ID, "','", 
                xy_tzzm$x, "','", xy_tzzm$y,"','", xy_tzzm$name,"','", 
                xy_tzzm$fwts,"','", xy_tzzm$zone,"')", collapse = ",")
sql <- paste0("INSERT into f_select (gid, id, x, y, name, fwts, zone) 
             values ", sqlv)
dbSendQuery(con, sql)
dbSendQuery(con, "VACUUM ANALYZE f_select")

# check if duplicated entries
if(any(xy_tzzm$name %in% xy_spzm$name)){
  stop("Duplicated F/N entries", call. = FALSE)
} 

# Update kml_data
sqlrt <-  paste0("('", xy_spzm$name, "', ", "'", "N","','", 
                 xy_spzm$fwts,"')", collapse = ",")
sql <- paste0("INSERT into kml_data (name, kml_type, fwts) values ", sqlrt)
dbSendQuery(con, sql)
sqlrt2 <-  paste0("('", xy_tzzm$name, "', ", "'", "F","','", 
                 xy_tzzm$fwts,"')", collapse = ",")
sql2 <- paste0("INSERT into kml_data (name, kml_type, fwts) values ", sqlrt2)
dbSendQuery(con, sql2)
dbSendQuery(con, "VACUUM ANALYZE kml_data")

# Update master grid so that these are no longer available for random selection
sqlrt <- paste0(" (", paste0("'", xy_all$name, "'", collapse = ","), ")")
sql <- paste0("UPDATE master_grid SET avail='F' WHERE name in ", sqlrt)        
dbSendQuery(con, sql)
dbSendQuery(con, "VACUUM ANALYZE master_grid")

# Update master_grid_counter
num <- dbGetQuery(con, 
                  "SELECT COUNT(avail) FROM master_grid WHERE avail='F'")$count
sql <- paste0("UPDATE master_grid_counter SET counter=", num, 
              " WHERE block=1")
dbSendQuery(con, sql)
dbSendQuery(con, "VACUUM ANALYZE master_grid_counter")
dbDisconnect(con)
