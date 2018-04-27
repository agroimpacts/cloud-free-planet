
# load_f_random.R
# Choose and load random fqaqc sites

## Clear console and load required packages
rm(list=ls(all=TRUE))
library(raster)
library(data.table)
library(rmapaccuracy)


## Hardcoded Values 
kml_type <- "F"  # Type of KML (N for non-QAQC)
diam <- 500
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
alb <- paste0("+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=25 ", 
              "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")


## Determine working directory and database
dinfo <- getDBName()  # pull working environment
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")

# Get a list of all proj4 strings by zone
sql <- paste0("select proj4text from spatial_ref_sys where auth_name='map_af' ",
              "order by auth_srid")
prjstr <- dbGetQuery(con, sql)$proj4text

# Select coordinates from points that are available
sql <- "select id, x, y, name, fwts, zone from master_grid where avail = 'T'"
xy_tab <- data.table(dbGetQuery(con, sql))

# Draw weighted random sample
fqaqc_n <- round(nrow(xy_tab) * 20 * 0.000005)  
set.seed(2)
xy_tabs <- xy_tab[{name %in% sample(name, size = fqaqc_n, replace = FALSE)}]
# xy_tabs[, hist(fwts, breaks = 0:10)]
# xy_tabs[fwts == 1, .N] / xy_tabs[fwts > 1, .N]

## Process points into kmls
# Convert point data to proper projections
gpnts <- sapply(1:nrow(xy_tabs), function(i) { 
  zn <- xy_tabs[i, zone]
  xy <- data.frame(xy_tabs[i, ])
  coordinates(xy) <- xy[2:3]
  xy <- xy[, 4:6]
  crs(xy) <- alb
  xy_trans <- spTransform(xy, CRS(prjstr[zn]))
})

# Convert points to polygons
gpols <- sapply(1:nrow(xy_tabs), function(i) { 
  xy_trans <- gpnts[[i]] 
  proj4 <- proj4string(xy_trans)
  ptdata <- data.frame(xy_trans)
  gpol <- point_to_gridpoly(xy = ptdata, w = diam, CRSobj = CRS(proj4))
  gpol@data$zone <- xy_trans@data$zone
  gpol@data$id <- i
  gpol <- spChFIDs(gpol, as.character(gpol@data$id))
})

# Transform to geographic coordinates and write out to kmls
data_path <- path.expand(paste0(dinfo["project.root"], "/kmls/"))
gpols_gcs <- sapply(1:length(gpols), function(i) {
  gpol_gcs <- spTransform(x = gpols[[i]], CRSobj = CRS(gcs))
  writeOGR(gpol_gcs, dsn = paste0(data_path, gpol_gcs$name, ".kml"), 
           layer = gpol_gcs$name, driver = "KML", overwrite = TRUE)
  gpol_gcs
})
gpols_gcs <- do.call(rbind, gpols_gcs)


## Update databases
# Create new table for fqaqc sites
dbRemoveTable(con, "fqaqc_sites")
sql <- paste("CREATE TABLE fqaqc_sites",
             "(gid integer PRIMARY KEY,",
             "id integer, x double precision,",
             "y double precision, name varchar,",
             "fwts integer, zone integer)")
dbSendQuery(con, sql)

# Upload data
sqlv <-  paste0("('", seq(1,fqaqc_n),"','", xy_tabs$id, "','", 
                xy_tabs$x, "','", xy_tabs$y,"','", xy_tabs$name,"','", 
                xy_tabs$fwts,"','", xy_tabs$zone,"')", collapse = ",")
sql <- paste("insert into fqaqc_sites (gid, id, x, y, name, fwts, zone) 
             values ", sqlv)
dbSendQuery(con, sql)
dbSendQuery(con, "VACUUM ANALYZE fqaqc_sites")

# Update master grid so that these are no longer available for random selection
sqlrt <- paste0(" (", paste0("'", xy_tabs$name, "'", collapse = ","), ")")
sql <- paste("UPDATE master_grid SET avail='F' where name in", sqlrt)        
dbSendQuery(con, sql)
dbSendQuery(con, "VACUUM ANALYZE master_grid")

# Update kml_data
sqlrt2 <-  paste0("('", xy_tabs$name, "', ", "'", kml_type,"','", 
                  xy_tabs$fwts,"')", collapse = ",")
sql <- paste("insert into kml_data (name, kml_type, fwts) values ", sqlrt2)
dbSendQuery(con, sql)
dbSendQuery(con, "VACUUM ANALYZE kml_data")

# Update master_grid_counter
num <- dbGetQuery(con, 
                  "SELECT COUNT(avail) FROM master_grid WHERE avail='F'")$count
sql <- paste0("UPDATE master_grid_counter SET counter=", num, 
              " WHERE block=1")
dbSendQuery(con, "VACUUM ANALYZE master_grid_counter")
dbSendQuery(con, sql)
dbDisconnect(con)