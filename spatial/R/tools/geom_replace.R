# geom_replace

# clean_geom.R
# fix a particular qaqc site

## Clear console and load required packages
rm(list=ls(all=TRUE))
library(raster)
library(rgeos)
library(rgdal)
library(rmapaccuracy)
library(yaml)

params <- yaml.load_file('../../../common/config.yaml')

# Static arguments
prjsrid <- 102022
count.err.wt <- 0.1  
in.err.wt <- 0.7  
out.err.wt <- 0.2  
err.switch <- 2  ### 2/6/15 changed to 2
comments <- "F"
write.err.db <- "T"  
draw.maps  <- "T"  
test <- "N"  
test.root <- "N"  
user <- params$mapper$db_username
password <- params$mapper$db_password
kmlid <- "SA226678"
assignmentid <- "zyqZQuEJ1yNX"
assignmentidtype <- "training_id"
tryid <- 1
mtype <- "tr"

# Paths and connections
dinfo <- getDBName()  # pull working environment
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = user, password = password)

# Get correct crs
prj.sql <- paste0("select proj4text from spatial_ref_sys where srid=", 
                  prjsrid)
prjstr <- dbGetQuery(con, prj.sql)$proj4text
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"


# Get old geometry
ewkt.sql <- paste0("SELECT gid,ST_AsEWKT(geom)", 
                   " from qual_user_maps WHERE name LIKE ", "'%", kmlid, 
                   "%' AND training_id=", "'", assignmentid, "'")
ewkt.tab <- dbGetQuery(con, ewkt.sql)
ewkt.tab[, 2] <- gsub("^SRID=*.*;", "", ewkt.tab[, 2])

# Fix with prepair and convert to polygons
polyfixes <- lapply(1:nrow(ewkt.tab), function(x) {
  ewkttofix <- ewkt.tab[x, ]
  ppath <- paste0(dinfo["project.root"], "/prepair")
  str <- paste0(ppath, "/prepair", " --wkt '", ewkttofix[, 2], 
                "' --minarea", " 0.000000001")
  ewktfix <- system(str, intern = TRUE)
  polyfix <- as(readWKT(ewktfix, p4s = prjstr), "SpatialPolygonsDataFrame")
  polyfix@data$ID <- ewkt.tab[x, 1]
  newid <- paste(x)
  polyfix <- spChFIDs(polyfix, newid)
  polyfix <- polyfix[, "ID", drop = "FALSE"]
})
spdffix <- do.call(rbind, polyfixes)

# Save as a shapefile and clean with pprepair
dsn <- paste0(dinfo["project.root"], "/spatial/data/cleaning/", 
              kmlid, ".shp")
dso <- paste0(dinfo["project.root"], "/spatial/data/cleaning/", 
              kmlid, "_clean" ,".shp") 
writeOGR(spdffix, dsn = dsn, layer = kmlid, 
         driver = "ESRI Shapefile", morphToESRI = TRUE)
ppcall <- paste0(dinfo["project.root"], "/pprepair/pprepair -i ", dsn, 
                 " -o ", dso, " -fix")
ctch <- system(ppcall, intern = TRUE)

# Recreate as a polygon and convert to WKT
clean.poly <- readOGR(dsn = dso, layer = paste0(kmlid, "_clean"))
crs(clean.poly) <- gcs
clean.poly <- spTransform(clean.poly, CRS(prjstr))
clean.poly <- clean.poly[, "ID", drop = "FALSE"]
st_asewkt <- writeWKT(clean.poly, byid = TRUE)
geom.new <- data.frame(clean.poly@data, st_asewkt)
geom.new[, 2] <- gsub("POLYGON ", paste0("SRID=", prjsrid,";MULTIPOLYGON("), 
                      geom.new[, 2])

# Update database
for(i in 1: nrow(geom.new)) {
  sql1 <- paste0("UPDATE qaqcfields SET geom = NULL WHERE name = '", kmlid, 
                 "' AND gid = '", geom.new[i, 1], "'")
  dbSendQuery(con, sql1)
  sql2 <- paste0("UPDATE qaqcfields SET geom = ST_GeomFromEWKT('", 
                 geom.new[i, 2], ")') WHERE name = '", kmlid, 
                 "' AND gid = '", geom.new[i, 1], "'")
  dbSendQuery(con, sql2)
}
