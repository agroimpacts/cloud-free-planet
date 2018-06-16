library(rgdal)
library(rgeos)
library(sf)
library(data.table)
library(dplyr)
library(raster)
library(lwgeom)
library(fasterize)

suppressMessages(library(rmapaccuracy)) # have to load this to get connection
output.heatmap <- FALSE # if output heat map
user <- "***REMOVED***"
password <- "***REMOVED***"
db.tester.name <- "sye"
alt.root <- NULL
host <- NULL
diam <- 0.005 / 2 ## new master grid diameter
riskpixelthres <- 0.4 # determine risk pixels that are larger than thres

qsite <- TRUE
min_mappedcount <- 0 # testlines
scorethres <- 0     # testlines
output.riskmap <- FALSE # testlines

gcsstr <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
prjstr <- paste0("+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=",
                 "25 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

load("/home/sye/olddatabase/allqs_with.rda")
allqs_with <- as.data.frame(allqs_with)

workers_scores <- allqs_with %>% filter(status == 'Approved')%>%
  group_by(worker_id) %>% 
  summarize(mean = mean(score))


coninfo <- mapper_connect(user = user, password = password,
                          db.tester.name = db.tester.name, 
                          alt.root = alt.root, host = host)

##################################### old qaqc maps########################
uniquenameid <- unique(allqs_with$name)
# kmlid <- 'ZA0268247'



hist_field_acc <- rep(0, 100)

hist_nofield_acc <- rep(0, 100)

for (i in 1:length(uniquenameid)){
  print(i)
  kmlid <- uniquenameid[i]
  cassign_geom <- allqs_with %>% filter(name == kmlid, 
                                        status == 'Approved') %>% dplyr::select(assignment_id, geom_clean)
  
  uniqueassignmentid <- unique(cassign_geom$assignment_id)
  
  uniqueworkerid <-sapply(1:length(uniqueassignmentid), function(x){
    worker_id<- allqs_with %>% filter(assignment_id == 
                                           uniqueassignmentid[x])%>% dplyr::select(worker_id)
    unique(worker_id$worker_id)
  })
  
  # read grid polygon
  xy_tabs <- data.table(tbl(coninfo$con, "master_grid") %>% 
                          filter(name == kmlid) %>% 
                          dplyr::select(x, y, name) %>% collect())
  # read grid geometry, and keep gcspl
  grid.poly <- point_to_gridpoly(xy = xy_tabs, w = diam, NewCRSobj = gcsstr, 
                                 OldCRSobj = gcsstr)
  grid.poly <- st_geometry(grid.poly)  # retain geometry only
  
  bayes.polys_o <- lapply(1:length(uniqueassignmentid), function(x){
    user.polys<- st_as_sf(cassign_geom %>% filter(assignment_id == uniqueassignmentid[x]),crs=gcsstr)
    user.hasfields <- ifelse(nrow(user.polys) > 0, "Y", "N")
    if (uniqueworkerid[x] %in% workers_scores$worker_id){
      # if user maps have field polygons
      if(user.hasfields == "Y") { 
        user.polys.valid <- st_make_valid(user.polys)
        # union user polygons
        user.poly <- suppressWarnings(st_union(st_collection_extract(user.polys.valid, c("POLYGON"))))
        
        score <- workers_scores[workers_scores$worker_id==uniqueworkerid[x],]$mean
        
        bayes.poly <- st_sf('posterior_field' = 1, 'posterior_nofield' =
                              1,'max_field_lklh' = score, 'max_nofield_lklh' =
                              score, 'prior'= score, 
                            geometry = st_sfc(user.poly))
        # set crs
        st_crs(bayes.poly) <- gcsstr
      }else{
        score <- workers_scores[workers_scores$worker_id==uniqueworkerid[x],]$mean
        # if users do not map field, set geometry as empty multipolygon
        bayes.poly <- st_sf('posterior_field' = 1, 'posterior_nofield' =
                              1,'max_field_lklh' = score, 'max_nofield_lklh' =
                              score, 'prior'= score,
                            geometry = st_sfc(st_multipolygon()))
        
        st_crs(bayes.poly) <- gcsstr
      }
      bayes.poly
    }
    
  })
  
  bayes.polys <- do.call(rbind, plyr::compact(bayes.polys_o))
  # if no any user map polygons for this grid or if for cvml training, 
  # use the grid extent as the raster extent
  # for Q sites, use the maximum combined boundary of all polygons and master grid
  # as the raster extent
  bb_grid <- st_bbox(grid.poly)
  bb_polys <- st_bbox(st_union(bayes.polys))
  new_bbbox <- st_bbox(c(xmin = min(bb_polys$xmin,bb_grid$xmin), 
                         xmax = max(bb_polys$xmax,bb_grid$xmax), 
                         ymax = max(bb_polys$ymax,bb_grid$ymax), 
                         ymin = min(bb_polys$ymin,bb_grid$ymin)), crs = gcsstr)
  rasterextent <- st_sf(geom = st_as_sfc(new_bbbox))
  
  bayesoutput_BMA <- BayesModelAveraging(bayes.polys = bayes.polys,
                                 rasterextent = rasterextent,
                                 threshold = 0.5)
  
  # bayesoutput_heatmap <- heatmapcreation(bayes.polys = bayes.polys,
  #                                rasterextent = rasterextent)
  # 
  # bayesoutput_bayesfusion <- bayesianfusion(bayes.polys = bayes.polys,
  #                               rasterextent = rasterextent)
  # 
  # plot(bayesoutput_bayesfusion$heatmap, main = 'bayesfusion')
  # plot(bayesoutput_heatmap, main = 'heatmap')
  # plot(bayesoutput_BMA, main = 'BMA')
  # bayesoutput <- bayesoutput_BMA$layer
  
  # riskpixelpercentage <- ncell(bayesoutput$riskmap
  #                                  [bayesoutput$riskmap > riskpixelthres])/
  #   (nrow(bayesoutput$riskmap)*
  #      ncol(bayesoutput$riskmap))
  
  qaqc.sql <- paste0("select gid from qaqcfields where name=", "'", kmlid, "'")
  qaqc.polys <- DBI::dbGetQuery(coninfo$con, qaqc.sql)
  qaqc.hasfields <- ifelse(nrow(qaqc.polys) > 0, "Y", "N") 
  if(qaqc.hasfields == "Y") {
    qaqc.sql <- paste0("select gid, geom_clean",
                       " from qaqcfields where name=", "'", kmlid, "'")
    qaqc.polys <- suppressWarnings(st_read(coninfo$con, query = qaqc.sql, 
                                           geom_column = 'geom_clean'))
  } 
  
  qaqc_rst <- raster(extent(as(rasterextent, 'Spatial')), 
                     resolution = 0.005/200, crs = gcsstr)
  
  
  qaqc_rst_field <- fasterize(qaqc.polys, qaqc_rst, 
                              background = 0)
  qaqc_rst_nofield <- 1 - qaqc_rst_field
  
  values(qaqc_rst_field)[values(qaqc_rst_field) == 0] = NA
  
  values(qaqc_rst_nofield)[values(qaqc_rst_nofield) == 0] = NA
  
  values(bayesoutput_BMA$heatmap)[values(bayesoutput_BMA$heatmap) == minValue(bayesoutput_BMA$heatmap)] = NA ##!
  
  heatfieldqaqc <- qaqc_rst_field * bayesoutput_BMA$heatmap 
  
  heatnofieldqaqc <- qaqc_rst_nofield * bayesoutput_BMA$heatmap 
  
  hist_field <- hist(heatfieldqaqc, breaks = c(0:100)/100)
  
  hist_nofield <- hist(heatnofieldqaqc, breaks = c(0:100)/100)
  
  hist_field_acc <- hist_field_acc + hist_field$counts
  
  hist_nofield_acc <- hist_nofield_acc + hist_nofield$counts
}

breaks = c(0:99)/100
csv<-data.frame(breaks, hist_field_acc, hist_nofield_acc)
write.table(csv, file = "/home/sye/olddatabase/bma_lklh_new.csv", sep = ",", col.names = NA,
         qmethod = "double")
# ###################################### thresholding ###########################
lklh_table <- read.table(file = "/home/sye/olddatabase/bma_lklh_new.csv", 
                          header = TRUE, sep = ",")
barplot(lklh_table$hist_field_acc)
sum_count_field <- sum(lklh_table$hist_field_acc)
sum_count_nofield <- sum(lklh_table$hist_nofield_acc)

error_lklh <- sapply(1:99, function(i){
  error <- sum(lklh_table[1 : i, ]$hist_field_acc)/sum_count_field + 
    sum(lklh_table[i+1 : (100-i), ]$hist_nofield_acc)/sum_count_nofield
  error
})

threshold <- lklh_table[which.min(error_lklh), ]$breaks + 0.01

h1<-lklh_table$hist_field_acc/sum(lklh_table$hist_field_acc)
h2<-lklh_table$hist_nofield_acc/sum(lklh_table$hist_nofield_acc)
names(h2) <- c(0:99)/100
barplot(h2, ylab = 'Frequency', xlab = 'P(L=field|D)', col="white", border = "green")
barplot(h1, col="white", border = "red", add=TRUE)
legend("center",
            legend = c("No field", "Field"), fill= c("white", "white"),
              border = c("green",
                            "red"))
####################################### old N/F sites
threshold <- 0.5
load("/home/sye/olddatabase/allqs_without.rda")
allqs_without <- as.data.frame(allqs_without)

uniquenameid_without <- unique((allqs_without %>% filter(status == 'Approved') 
                               %>% dplyr::select(name))$name)

risk_percentage <-rep(0, length(uniquenameid_without))

risk_percentage <- sapply (1:(length(uniquenameid_without)), function(i){
  kmlid <- uniquenameid_without[i]
  print(i)
  # kmlid <- 'ZA0268247'
  
  cassign_geom <- allqs_without %>% filter(name == kmlid, 
                                        status == 'Approved') %>% dplyr::select(assignment_id, geom_clean)
  
  uniqueassignmentid <- unique(cassign_geom$assignment_id)
  
  uniqueworkerid <-sapply(1:length(uniqueassignmentid), function(x){
    worker_id<- allqs_without %>% filter(assignment_id == 
                                        uniqueassignmentid[x])%>% dplyr::select(worker_id)
    unique(worker_id$worker_id)
  })
  
  # read grid polygon
  xy_tabs <- data.table(tbl(coninfo$con, "master_grid") %>% 
                          filter(name == kmlid) %>% 
                          dplyr::select(x, y, name) %>% collect())
  # read grid geometry, and keep gcspl
  grid.poly <- point_to_gridpoly(xy = xy_tabs, w = diam, NewCRSobj = gcsstr, 
                                 OldCRSobj = gcsstr)
  grid.poly <- st_geometry(grid.poly)  # retain geometry only
  
  bayes.polys_o <- lapply(1:length(uniqueassignmentid), function(x){
    user.polys<- st_as_sf(cassign_geom %>% filter(assignment_id == uniqueassignmentid[x]),crs=gcsstr)
    user.hasfields <- ifelse(nrow(user.polys) > 0, "Y", "N")
    if (uniqueworkerid[x] %in% workers_scores$worker_id){
      # if user maps have field polygons
      if(user.hasfields == "Y") { 
        user.polys.valid <- st_make_valid(user.polys)
        # union user polygons
        user.poly <- suppressWarnings(st_union(st_collection_extract(user.polys.valid, c("POLYGON"))))
        
        score <- workers_scores[workers_scores$worker_id==uniqueworkerid[x],]$mean
        
        bayes.poly <- st_sf('posterior_field' = 1, 'posterior_nofield' =
                              1,'max_field_lklh' = score, 'max_nofield_lklh' =
                              score, 'prior'= score, 
                            geometry = st_sfc(user.poly))
        # set crs
        st_crs(bayes.poly) <- gcsstr
      }else{
        score <- workers_scores[workers_scores$worker_id==uniqueworkerid[x],]$mean
        # if users do not map field, set geometry as empty multipolygon
        bayes.poly <- st_sf('posterior_field' = 1, 'posterior_nofield' =
                              1,'max_field_lklh' = score, 'max_nofield_lklh' =
                              score, 'prior'= score,
                            geometry = st_sfc(st_multipolygon()))
        
        st_crs(bayes.poly) <- gcsstr
      }
      bayes.poly
    }
    
  })
  
  bayes.polys <- do.call(rbind, plyr::compact(bayes.polys_o))
  
  if (nrow(bayes.polys)==0){
    stop("There is not enough valid assignments (> minimum score)")
  }
  
  # count the number of user maps that has field polygons
  count_hasuserpolymap <- length(which(st_is_empty(bayes.polys[, "geometry"]) ==
                                         FALSE))
  
  # if no any user map polygons for this grid or if for cvml training, 
  # use the grid extent as the raster extent
  # for Q sites, use the maximum combined boundary of all polygons and master grid
  # as the raster extent
  bb_polys <- st_bbox(st_union(bayes.polys))
  rasterextent <- st_sf(geom = st_as_sfc(bb_polys))
  bayesoutput_BMA <- BayesModelAveraging(bayes.polys = bayes.polys,
                                         rasterextent = rasterextent, 
                                         threshold = threshold)
  
  writeRaster(bayesoutput_BMA$heatmap, paste0("/home/sye/olddatabase/consensus_oldmaps/heatmap/", 
                              kmlid, "_heatmap.tif"), overwrite=TRUE)
   
  writeRaster(bayesoutput_BMA$labelmap, paste0("/home/sye/olddatabase/consensus_oldmaps/labelmap/", 
                                      kmlid, "_labelmap.tif"), overwrite=TRUE)
  
  
  riskpixelpercentage <- ncell(bayesoutput_BMA$riskmap
                                   [bayesoutput_BMA$riskmap > riskpixelthres])/
   (nrow(bayesoutput_BMA$riskmap)*
      ncol(bayesoutput_BMA$riskmap))
  riskpixelpercentage  
})

csv<-data.frame(risk_percentage, uniquenameid_without)
write.table(csv, file = "/home/sye/olddatabase/consensus_oldmaps/risk_table_new_T05.csv", 
            sep = ",", col.names = NA,
                           qmethod = "double")
##########################Convert to vectors##########################
require("igraph")
require("smoothr")
library(RPostgreSQL)

load("/home/sye/olddatabase/allqs_without.rda")
uniquenameid_without <- unique((allqs_without %>% filter(status == 'Approved') 
                                %>% dplyr::select(name))$name)
allqs_without <- as.data.frame(allqs_without)

gid <- 0
for (j in 1: length(uniquenameid_without)){
  print(j)
  kmlid <- uniquenameid_without[j]
  
  labelmap <- raster(file.path(paste0("/home/sye/olddatabase/consensus_oldmaps/labelmap/", 
                                      kmlid, "_labelmap.tif")))
  # NAvalue(labelmap) <- 0
  #polygon_sp <- rasterToPolygons(labelmap, n=4, dissolve = TRUE, na.rm = TRUE)
  polygon_sp <- gdal_polygonizeR(labelmap)
  names(polygon_sp)<-"value"
  polygon_sp_simplify <- gSimplify(polygon_sp, tol = 0.00005, topologyPreserve = TRUE)
  polygon_sf <- SpatialPolygonsDataFrame(polygon_sp_simplify, 
                                         data = as.data.frame
                                         (polygon_sp$value), 
                                         match.ID = F) %>% st_as_sf %>% st_cast("POLYGON")
  
  # exclude background polygon, and convert to sfc
  polygon_sfc_field <- polygon_sf[polygon_sf$polygon_sp.value!=0,]$geometry
  
  # set threshold as 80 square meters
  thres <- 80
  r_poly_dropped <- drop_crumbs(polygon_sfc_field, thres)
  p_dropped <- fill_holes(r_poly_dropped, threshold = thres)
  polygon_sfc_valid <-st_make_valid(p_dropped) %>% 
    st_collection_extract(c("POLYGON")) %>% smooth(method = "chaikin")
  
  risk_table <- read.table(file = "/home/sye/olddatabase/consensus_oldmaps/risk_table_new_T05.csv",
                           header = TRUE, sep = ",")
  risk <- risk_table[uniquenameid_without==kmlid, ]$risk_percentage
  
  for (i in 1: length(polygon_sfc_valid)){
    gid <- gid + 1
    polygons_wkt <- st_as_text(polygon_sfc_valid[i], EWKT=TRUE)
    poly.sql <- paste0("insert into qaqcfields_fromoldmaps (name ,", 
                       "geom_clean, gid, category, categ_comment, risk_percentage)",
                       " values ('", kmlid, "', ", "ST_GeomFromEWKT('", polygons_wkt, "'), ",  gid, 
                       ", 'NULL'", ", 'NULL', ", risk, ")")
    ret <- dbSendQuery(coninfo$con, poly.sql)
  }
  
}

#######################
j<-10
kmlid <- uniquenameid_without[j]
kmlid <- "ZA3919948"
qaqc.sql <- paste0("select gid from qaqcfields_fromoldmaps where name=", "'", kmlid, "'")
qaqc.polys <- DBI::dbGetQuery(coninfo$con, qaqc.sql)
qaqc.hasfields <- ifelse(nrow(qaqc.polys) > 0, "Y", "N") 
if(qaqc.hasfields == "Y") {
  qaqc.sql <- paste0("select gid, geom_clean",
                     " from qaqcfields_fromoldmaps where name=", "'", kmlid, "'")
  qaqc.polys <- suppressWarnings(st_read(coninfo$con, query = qaqc.sql, 
                                         geom_column = 'geom_clean'))
  qaqc.polys <- st_transform(qaqc.polys, crs=prjstr)
  qaqc.polys <- st_buffer(qaqc.polys, 0)
} 
plot(qaqc.polys)

# csv<-data.frame(breaks, hist_field_acc, hist_nofield_acc)
# write.table(csv, file = "/home/sye/olddatabase/bma_lklh.csv", sep = ",", col.names = NA,
#               +             qmethod = "double")

# writeRaster(bayesoutput$heatmap, paste0("/home/sye/consensusmap/qsites/", kmlid, "_heatmap.tif"))
# st_write(qaqc.polys, paste0("/home/sye/consensusmap/qsites/", kmlid, "_qaqc.shp"))

# csv<-data.frame(breaks, hist_field_acc, hist_nofield_acc)
# write.table(csv, file = "/home/sye/olddatabase/bma_lklh.csv", sep = ",", col.names = NA,
#               +             qmethod = "double")

