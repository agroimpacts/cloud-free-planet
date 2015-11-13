
#Selection of sites for F QAQC type assignments/HITs, from the master_grid, and the corresponding creation of a new database to hold them.

prjsrid   <- 102022  # EPSG identifier for equal area project
fname <- "KMLgenerate"  # KMLgenerate 
kml_type <- "F"  # Type of KML (N for non-QAQC)
diam <- 500
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

library(RPostgreSQL)
library(rmapaccuracy)
library(data.table)

# Determine working directory and database
dinfo <- getDBName()  # pull working environment

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")

sql <- paste0("select proj4text from spatial_ref_sys where srid=", prjsrid)
prjstr <- dbGetQuery(con, sql)$proj4text

# sql <- "select name from master_grid where avail = 'T'"
# grid_names <- dbGetQuery(con, sql)$name
sql <- "select name, x, y, fwts from master_grid where avail = 'T'"
xy_tab <- data.table(dbGetQuery(con, sql))

#Pull out a sample of cells representing some proportion of Africa\'s area--here 1/4 of 1/10 of a percent gives a manageable number of sites

fqaqc_n <- round(nrow(xy_tab) * 20 * 0.00002)  

# Step 2. Draw weighted random sample
# Just an ordinary random sample to select cells, because the weighted
# draw was already made in creating master_grid
set.seed(2)
xy_tabs <- xy_tab[{name %in% sample(name, size = fqaqc_n, replace = FALSE)}]
# xy_tabs2 <- xy_tabs  # if want to check random draw consistency
# xy_tabs2$name %in% xy_tabs$name
xy_tabs[, hist(fwts)]
xy_tabs[fwts == 1, .N] / xy_tabs[fwts > 1, .N]

# Convert them to polygons
gpols <- point_to_gridpoly(xy = data.frame(xy_tabs), w = diam, 
                           CRSobj = CRS(prjstr))

#Then write to shapefile, and load into new table in database

data_path <- paste0(dinfo["project.root"], "/data/fqaqc_sites.shp")
rgdal::writeOGR(gpols, dsn = data_path, gsub("\\.shp", "", basename(data_path)), driver = "ESRI Shapefile", overwrite = TRUE)

# save first fqaqc_sites table made, just to compare site selection in first
# draw and new draw replacing it
# alter_name <- "fqaqc_sites"
# new_name <- "fqaqc_sites_old"
# sql <- paste0("CREATE TABLE ", new_name, " AS TABLE ", alter_name)
# print(sql)
# dbSendQuery(con, sql)
# sql <- paste0("ALTER TABLE ", new_name, " ADD PRIMARY KEY (gid)")
# dbSendQuery(con, sql)
# dbRemoveTable(con, alter_name)

sql <- paste("shp2pgsql -s 102022 -g geom", data_path, 
             "fqaqc_sites | psql -U ***REMOVED*** -d SouthAfricaSandbox")
system(sql, intern = TRUE)


#Write into master grid that these are no longer available for random selection

sqlrt <- paste0(" (", paste0("'", xy_tabs[, name], "'", collapse = ","), ")")
sql <- paste("UPDATE master_grid SET avail='F' where name in", sqlrt)        
dbSendQuery(con, sql)
dbSendQuery(con, "VACUUM ANALYZE master_grid")


#Transform to geographic coordinates and write out to kmls
gpols_gcs <- spTransform(x = gpols, CRSobj = CRS(gcs))
for(i in 1:nrow(gpols_gcs)) {
  kml_name <- paste0(dinfo["project.root"], "/kmls/", gpols_gcs$name[i], ".kml")
  rgdal::writeOGR(gpols_gcs[i, ], dsn = kml_name, layer = gpols_gcs$name[i], 
                  driver = "KML", overwrite = TRUE)
  print(paste("kml for", kml_name, "written"))
}


#Add kml names to kml_data, with type = "F". First have to change the check constraint in the table
sql <- "ALTER TABLE kml_data DROP CONSTRAINT kml_type_check"
dbSendQuery(con, sql)  # drop
sql <- paste("ALTER TABLE kml_data ADD CONSTRAINT kml_type_check", 
             "CHECK (kml_type = ANY (ARRAY['N'::bpchar, 'Q'::bpchar,", 
             "'I'::bpchar, 'F'::bpchar]))")
dbSendQuery(con, sql)  # then add back updated check constraint
sqlrt2 <-  paste0("('", gpols_gcs$name, "', ", "'", kml_type,"','", gpols_gcs$fwts,"')", collapse = ",")

sql <- paste("insert into kml_data (name, kml_type, fwts) values ", sqlrt2)
dbSendQuery(con, sql)

#Finally, update master grid counter to show that this number of records is processed already
sql <- paste0("UPDATE master_grid_counter SET counter=", fqaqc_n, 
              " WHERE block=1")
dbSendQuery(con, sql)


