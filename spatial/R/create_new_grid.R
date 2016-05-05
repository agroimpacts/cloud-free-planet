# create_new_grid.R
# Create new grid for all of Africa


## Clear console and load required packages
rm(list=ls(all=TRUE))
library(raster)
library(rgdal)
library(rgeos)
library(gdalUtils)
library(rworldmap)
library(rworldxtra)
library(data.table)
library(dismo)
library(dtraster)
library(wrswoR)
library(RPostgreSQL)
library(rmapaccuracy)


## Set working directory and raster storage
setwd(paste0(getDBName()[2], "/spatial/data"))
rasterOptions(tmpdir = paste0(getwd(), "/tempraster"))


## Define functions
# make a proj4string for custom albers projections
make_p4s <- function(pcode = "aea", sp1, sp2, lat_orig, meridian, x_0 = 0, 
                     y_0 = 0, datum = "WGS84", units = "m", 
                     defs = "no_defs", ellps = "WGS84", 
                     towgs84 = "0,0,0") {
  plist <- list("projection" = c("+proj=", pcode), 
                "sp1" = c("+lat_1=", sp1), 
                "sp2" = c("+lat_2=", sp2),
                "lat_orig" = c("+lat_0=", lat_orig),
                "meridian" = c("+lon_0=", meridian),
                "x_0" = c("+x_0=", x_0), 
                "y_0" = c("+y_0=", y_0),
                "datum" = c("+datum=", datum), 
                "units" = c("+units=", units),
                "defs" = paste0("+", defs),
                "ellps" = c("+ellps=", ellps),
                "towgs84" = c("+towgs84=", towgs84))
  
  p4s <- paste(unname(sapply(plist, function(x) paste(x, collapse = ""))), 
               collapse = " ")
  return(p4s)
}

# function to generate custom albers projections proj4 string, based on standard
# parallels, meridian, and latitude of origin calculated from polygon 
# extents
custom_alb <- function(x, par_offset = 1 / 7) {
  p4s <- sapply(1:nrow(x), function(i) {  # i <- 1
    e <- bbox(x[i, ])[c(1, 3, 2, 4)]
    merid <- e[1] + diff(e[1:2]) / 2  # meridian 
    lat_orig <- e[3] + diff(e[3:4]) / 2  # latitude of origin
    poff <- round((diff(e[3:4]) * par_offset) / 0.5) * 0.5
    p1 <- e[4] - poff  # 1st standard parallel
    p2 <- e[3] + poff  # 2nd 
    make_p4s("aea", sp1 = p1, sp2 = p2, lat_orig = lat_orig, meridian = merid)
  })
  return(p4s)
}


## Define separate projection zones
# get map of Africa
map <- getMap(resolution = "li")
africa <- map[which(map@data$REGION == "Africa"), ]
gcs <- africa@proj4string

# Buffer slightly
alb <- paste0("+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=25 ", 
              "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")
af_alb <- spTransform(africa, CRS(alb))
mp_alb <- spTransform(africa[africa@data$SOVEREIGNT == "Madagascar", ], CRS(alb))
afbuf_alb <- gBuffer(af_alb, width = 10000)  # buffer by 10 km
mpbuf_alb <- gBuffer(mp_alb, width = 5000)  # buffer by 5 km
afbuf_gcs <- spTransform(afbuf_alb, gcs)
mpbuf_gcs <- spTransform(mpbuf_alb, gcs)

# find dimensions
dims <- bbox(afbuf_gcs)[c(1, 3, 2, 4)]
fl <- list(floor, ceiling, floor, ceiling)
afdims_e <- sapply(1:4, function(x) fl[[x]](dims[x]))  # expand to degree

# Create zone map
r <- raster(extent(afdims_e))
yres <- diff(afdims_e[3:4]) / 7
xres <- diff(afdims_e[1:2]) / 9
res(r) <- c(xres, yres)
r[] <- 1:ncell(r)
zones_gcs <- rasterToPolygons(r)
zones_gcs@proj4string <- gcs
zones_gcs <- spTransform(zones_gcs, gcs)

# Intersect with continent, discard non-intersecting zones
africau <- africa[africa@data$SOVEREIGNT != "Madagascar", ]  # exclude Madagas.
africau <- gUnaryUnion(africau)
zones_gcs <- zones_gcs[which(gIntersects(zones_gcs, africau, byid = TRUE)), ]
zones_gcs$zone <- as.numeric(1:nrow(zones_gcs))
zones_gcs <- spChFIDs(zones_gcs, as.character(1:nrow(zones_gcs)))
zones_gcs@data <- zones_gcs@data[, "zone", drop = FALSE]

# Separate region for Madagascar
dims <- bbox(mpbuf_gcs)[c(1, 3, 2, 4)]
dims_e <- sapply(1:4, function(x) fl[[x]](dims[x]))  # expand to degree
mp <- as(extent(dims_e), "SpatialPolygons")
mp@proj4string <- gcs
mp <- spTransform(mp, gcs)
mp <- as(mp, "SpatialPolygonsDataFrame")
mp$zone <- as.numeric(nrow(zones_gcs) + 1)
mp <- spChFIDs(mp, as.character(mp$zone))
mp@data <- mp@data[, "zone", drop = FALSE]
zones_gcs <- rbind(zones_gcs, mp)

# Remove overlap between Madagascar grid and others
zclps <- list(zones_gcs[38, ], zones_gcs[43, ])
clps <- lapply(1:length(zclps), function(i) {
  zclp <- zclps[[i]]
  clp <- as(gDifference(zclp, zones_gcs[47, ]), "SpatialPolygons")
  clp@proj4string <- gcs
  clp <- as(clp, "SpatialPolygonsDataFrame")
  clp$zone <- as.numeric(zclp$zone)
  clp <- spChFIDs(clp, as.character(clp$zone))
  clp@data <- clp@data[, "zone", drop = FALSE]
  clp
})
zones_gcs <- rbind(zones_gcs[1:37, ], clps[[1]],  zones_gcs[39:42, ], 
                   clps[[2]], zones_gcs[44:length(zones_gcs), ])


## Create Custom projections
setwd(paste0(getDBName()[2], "/spatial/data/gridfiles"))
p4s_zone <- custom_alb(zones_gcs)
write(p4s_zone, file = "proj4_strings.txt")

# Remove previous proj4 entries in database
dinfo <- getDBName()  # pull working environment
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")
for(i in 1:length(p4s_zone)) {
  sql <- paste0("DELETE FROM spatial_ref_sys WHERE srid=9", i, ";")
  dbSendQuery(con, sql)
}
dbDisconnect(con)

# Upload new entries
system(paste0("python ", getDBName()[2], "/spatial/python/proj4_insert.py"))
setwd(paste0(getDBName()[2], "/spatial/data"))


## Create Grid in Albers Africa Projection
# Get detailed map of Africa
map <- getMap(resolution = "high")
af_cnt <- map[which(map@data$REGION == "Africa"), ]
isl <-c("Cape Verde", "Mauritius", "Saint Helena", "Sao Tome and Principe",
        "Seychelles", "Comoros")  # list minor islands
af_cnt <- af_cnt[!af_cnt@data$SOVEREIGNT %in% isl, ]  # exclude minor islands
af_cnt@proj4string <- zones_gcs@proj4string
af_cnt <- crop(af_cnt, zones_gcs)
af_cnt_alb <- spTransform(af_cnt, CRS(alb))  # transform to Albers

# Dissolve countries
af_alb <- gUnaryUnion(af_cnt_alb)  
af_alb <- SpatialPolygonsDataFrame(af_alb, data = data.frame("ID" = 1), 
                                   match.ID = FALSE)

# Buffer
afbuf_alb <- gBuffer(af_alb, width = 1000)  # buffer by 1 km
afbuf_alb <- SpatialPolygonsDataFrame(afbuf_alb, data = data.frame("ID" = 1), 
                                      match.ID = FALSE)

# Transform Zones
zones_alb <- spTransform(zones_gcs, CRS(alb))

# Save shapes to file
sfile <- paste0(getwd(), "/shapes")
writeOGR(zones_gcs, dsn = paste0(sfile, "/zones_gcs.sqlite"), 
         layer = "zones_gcs", driver = "SQLite", 
         dataset_options = c("SPATIALITE = yes"))
writeOGR(af_cnt_alb, dsn = paste0(sfile, "/africa_countries_alb.sqlite"), 
         layer = "africa_countries_alb", driver = "SQLite", 
         dataset_options = c("SPATIALITE = yes")) 
writeOGR(af_alb, dsn = paste0(sfile, "/africa_alb.sqlite"), 
         layer = "africa_alb", driver = "SQLite", 
         dataset_options = c("SPATIALITE = yes"))
writeOGR(afbuf_alb, dsn = paste0(sfile, "/africa_alb_1km_buff.sqlite"), 
         layer = "afbuf", driver = "SQLite", 
         dataset_options = c("SPATIALITE = yes"))
writeOGR(zones_alb, dsn = paste0(sfile, "/zones_alb.sqlite"), 
         layer = "zones_alb", driver = "SQLite", 
         dataset_options = c("SPATIALITE = yes"))

# Grid the buffered shape         
gdal_rasterize(src_datasource = paste0(sfile, "/africa_alb_1km_buff.sqlite"),
               ot = "Int16", tr = c(1000, 1000), at = TRUE, a_nodata = 0,  
               dst_filename = paste0(sfile, "/buffrast.tif"),
               burn = 1, l = "afbuf", of = "GTiff")
afgridbuf <- raster(paste0(sfile, "/buffrast.tif"))
cells <- Which(!is.na(afgridbuf), cells = TRUE)
ids <- 1:length(cells)
afgrid <- afgridbuf
afgrid[cells] <- ids
afgrid <- writeRaster(afgrid, overwrite = TRUE, 
                      filename = paste0(sfile, "/africa_master_grid.tif"))

# Process cropland data for sample weights
fsrc <- paste0(getwd(), "/croplandv8/Hybrid_14052014V8.img")
gdalwarp(srcfile =  fsrc, t_srs = projection(afgrid), 
         dstfile = paste0(sfile, "/af_cropland.tif"), r = "bilinear", 
         ot = "Float32", te = bbox(afgrid)[1:4], dstnodata = -32768, 
         tr = res(afgrid), of = "GTiff", verbose = TRUE, overwrite = TRUE)
cropland <- raster(paste0(sfile, "/af_cropland.tif"))
cropland_p <- cropland / 100 * afgridbuf
cropland_p <- writeRaster(cropland_p, overwrite = TRUE, 
                          filename = paste0(sfile, "/af_cropland_prob.tif"))
recl <- cbind(seq(0, 1, 0.1)[-11], seq(0, 1, 0.1)[-1], 1:10)
cropland_pcl <- reclassify(cropland_p, rcl = recl, include.lowest = TRUE, 
                           filename = paste0(sfile, "/af_cropland_prob_cl.tif"),
                           overwrite = TRUE)
file.remove(paste0(sfile, "/buffrast.tif"))
file.remove(paste0(sfile, "/af_cropland.tif"))

# Import country data
gdal_rasterize(src_datasource = paste0(sfile, "/africa_countries_alb.sqlite"), 
               dst_filename = paste0(sfile, "/africa_countries_alb.tif"), 
               at = TRUE, ot = "Int16", a = "OID_", l = "africa_countries_alb", 
               tr = res(afgrid), verbose = TRUE, te = bbox(afgrid)[1:4], 
               a_nodata = -32768, of = "GTiff")
cntr <- raster(paste0(sfile, "/africa_countries_alb.tif"))
cntrm  <- cntr >= 1
afgridr <- afgrid * cntrm
cropland_pr <- cropland_p * cntrm

# Assign zone to each grid cell
gdal_rasterize(src_datasource = paste0(sfile, "/zones_alb.sqlite"), 
               dst_filename = paste0(sfile, "/zones_alb.tif"), at = TRUE, 
               ot = "Int16", a = "zone", l = "zones_alb", 
               tr = res(afgrid), verbose = TRUE, te = bbox(afgrid)[1:4], 
               a_nodata = -32768, of = "GTiff")
afzns <- raster(paste0(sfile, "/zones_alb.tif"))
cna <- Which(is.na(afgridr), cells = TRUE)
afzns[cna] <- NA

# Create Raster Brick
st <- stack(list(afgridr, cropland_pr, cropland_pcl, cntr, afzns))
br <- brick(st, filename = paste0(sfile, "/africa_master_brick.tif"), 
            overwrite = TRUE)

# Remove all files
rm(list=ls(all=TRUE))


## Create master grid as data table
# Reload becessary files
sfile <- paste0(getwd(), "/shapes")
br <- brick(paste0(sfile, "/africa_master_brick.tif"))
af_cnt_alb <- readOGR(dsn = paste0(sfile, "/africa_countries_alb.sqlite"), 
                      layer = "africa_countries_alb")
# Organize country data
af_cnt_dt <- data.table(af_cnt_alb@data[, c("oid_", "iso_a2")], 
                        key = "oid_")
setnames(af_cnt_dt, "oid_", "cnt_code")
setnames(af_cnt_dt, "iso_a2", "iso2")
af_cnt_dt <- af_cnt_dt[1:2, iso2 := c("SM", "WS")] # Create new ISO2 codes 

# Organize master grid
br_dt <- as.data.table.raster(br, xy = TRUE, progress = "text")
setnames(br_dt, old = colnames(br_dt)[3:7], 
         new = c("ID", "pr", "fwts", "cnt_code", "zone"))
br_dt <- br_dt[!is.na(ID)]
for(i in unique(br_dt$cnt_code)) {
  ind <- which(br_dt$cnt_code == i)
  br_dt[ind, ind := order(ind)]
}
setkey(br_dt, cnt_code)
mgrid <- merge(br_dt, af_cnt_dt, by = "cnt_code")
ndig <- nchar(max(mgrid$ind))
mgrid <- mgrid[, name := sprintf(paste0("%s%0", ndig, "i"), iso2, ind)]
setcolorder(mgrid, c("ID", "x", "y", "name", "pr", "fwts", "zone", "cnt_code", 
                     "iso2", "ind"))
mgrid <- mgrid[, (c("cnt_code", "iso2", "ind")) := NULL]

# Change data types and save to file
names_int <- c("ID", "fwts")
for(col in names_int) set(mgrid, j = col, value = as.integer(mgrid[[col]]))
mgrid <- mgrid[, avail := rep("T", nrow(mgrid))]
write.table(mgrid, file = "gridfiles/africa_master_grid.csv", sep = ",", 
            col.names = TRUE, row.names = FALSE)


## Divide up the master grid
# Set up row blocks per raster blockSize
b <- 20  # we want random draws of 5% of Africa
size <- ceiling(nrow(mgrid) / b)
row <- (0:(b - 1)) * size + 1
nrows <- rep(size, length(row))
dif <- b * size - nrow(mgrid)
nrows[length(nrows)]  <-  nrows[length(nrows)] - dif
bs <- list(row = row, nrows = nrows, n = b)
samp_tab <- cbind.data.frame("block" = 1:bs$n, "nrows" = as.integer(bs$nrows),
                             "counter" = as.integer(rep(0, bs$n)))

# Create output CSV files representing blocks of random draws
set.seed(234)
for(i in samp_tab$block) {
  print(i)
  n <- nrow(mgrid)
  og <- mgrid[sample_int_rej(n, size = samp_tab$nrows[i], prob = fwts), ]
  mgrid <- mgrid[!ID %in% og[, ID]]
  print(paste("rows in sub-grid =", nrow(og), " - rows in master =", 
              nrow(mgrid), "common rows in both is none:", 
              any(mgrid[, ID] %in% og[, ID])))
  onm <- paste0("gridfiles/africa_master_grid_sub", i, ".csv")
  write.table(og, file = onm, sep = ",", col.names = TRUE, row.names = FALSE)
}


## Delete and remake grid tables
# Master Grid Table
dinfo <- getDBName()  # pull working environment
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")

dbRemoveTable(con, name = "master_grid")
sql <- paste("CREATE TABLE master_grid",
             "(gid serial PRIMARY KEY,",
             "id integer, x double precision,",
             "y double precision, name varchar, pr double precision,", 
             "fwts integer, zone integer, avail char(1))")
dbSendQuery(con, sql)
dbSendQuery(con, paste0("CREATE INDEX name_gix ON master_grid (id, name, ", 
                        "fwts, zone, avail)"))
dbSendQuery(con, "VACUUM ANALYZE master_grid")
dbSendQuery(con, "CLUSTER master_grid USING name_gix")

# Master Grid Counter Table
dbRemoveTable(con, name = "master_grid_counter")
dbWriteTable(con, name = "master_grid_counter", value = samp_tab, row.names = 0)
sql <- "ALTER TABLE master_grid_counter ADD PRIMARY KEY (block)"
dbSendQuery(con, sql)
dbSendQuery(con, "VACUUM ANALYZE master_grid_counter")
dbDisconnect(con)