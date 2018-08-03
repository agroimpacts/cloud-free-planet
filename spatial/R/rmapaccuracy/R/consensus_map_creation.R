#' Control the output of label maps, risk maps, and heat maps 
#' @param kmlid 
#' @param min.mappedcount the minimum approved assignment count
#' @param kml.usage the use of kml, could be 'train, 'test' or 'holdout';
#' This parameter will determine the directory of S3 folder to store consensus 
#' maps.
#' @param riskthres the threshold to select 'risk' pixels
#' @param user User name for database connection
#' @param password Password for database connection
#' @param db.tester.name User name for testing (default NULL)
#' @param alt.root Alternative location for writing out maps (default NULL)
#' @param host NULL or "crowdmapper.org", if testing from remote location
#' @return Sticks conflict/risk percentage pixels into database (kml_data) and
#' (pending) writes rasters to S3 bucket
#' @export
#' 
consensus_map_creation <- function(kmlid, min.mappedcount, kml.usage,
                                   output.riskmap, riskpixelthres, diam, 
                                   user, password, db.tester.name, alt.root, 
                                   host, qsite = FALSE) {
  
  coninfo <- mapper_connect(user = user, password = password,
                            db.tester.name = db.tester.name, 
                            alt.root = alt.root, host = host)
  # prjstr <- as.character(tbl(coninfo$con, "spatial_ref_sys") %>% 
  #                          filter(srid == prjsrid) %>% 
  #                          select(proj4text) %>% collect())
  gcsstr <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
  
  # query hitid
  hit.sql <- paste0("select hit_id from hit_data where name = '", kmlid, "'")
  hitid <- (DBI::dbGetQuery(coninfo$con, hit.sql))$hit_id
  
  # query mtype
  # mtype.sql <- paste0("select kml_type from kml_data where name = '",kmlid, "'")
  # mtype <- (DBI::dbGetQuery(coninfo$con, mtype.sql))$kml_type
  
  # query mappedcount
  mappedcount.sql <- paste0("select mapped_count from kml_data where name = '",
                            kmlid, "'")
  mappedcount <- as.numeric((DBI::dbGetQuery(coninfo$con, 
                                             mappedcount.sql))$mapped_count)
 
  if (mappedcount < min.mappedcount) {
    stop("there is not enough approved assignment for creating consensus maps")
  }

  
  # query assignmentid flagged as 'approved'
  assignment.sql <- paste0("select assignment_id from assignment_data", 
                           " where hit_id ='", hitid, 
                           "' and status = 'Approved'", 
                           " order by assignment_id")  
  
  assignmentid <- (DBI::dbGetQuery(coninfo$con, assignment.sql))$assignment_id
  
  # read grid polygon
  xy.tabs <- data.table(tbl(coninfo$con, "master_grid") %>% 
                          filter(name == kmlid) %>% 
                          dplyr::select(x, y, name) %>% collect())
  # read grid geometry, and keep gcs
  grid.poly <- point_to_gridpoly(xy = xy.tabs, w = diam, NewCRSobj = gcsstr, 
                                 OldCRSobj = gcsstr)
  grid.poly <- st_geometry(grid.poly)  # retain geometry only
  
  # lklh_field: p(user=field|groundtruth=field)
  # lklh_nofield: p(user=no field|groundtruth=no field)
  # Read user fields, field and no field likelihood from database into sf object
  bayes.polys <- lapply(assignmentid, function(x) {
    # workerid
    workerid.sql <- paste0("select worker_id from assignment_data", 
                           " where assignment_id ='", x, 
                           "' order by assignment_id")
    workerid <- (DBI::dbGetQuery(coninfo$con, workerid.sql))$worker_id
      
    # read all scored assignments including 'Approved' and 'Rejected'
    # for calculating history field and no field likelihood of worker i
    histassignid.sql <- paste0("select assignment_id from", 
                               " assignment_data where worker_id = '", 
                               workerid, "'",
                               " and (status = 'Approved' OR status = ",
                               "'Rejected') and score IS NOT NULL")
    historyassignmentid <- suppressWarnings(DBI::dbGetQuery(coninfo$con, 
                                             histassignid.sql)$assignment_id)
    
    # read all valid likelihood and score from history assignments
    userhistories <- lapply(c(1:length(historyassignmentid)), function(x) {
   
      # need add field_skill and nofield_skill columns to new_error_data tables
      likelihood.sql <- paste0("select new_score, field_skill, nofield_skill",
                               " from new_error_data  where assignment_id  = '", 
                               historyassignmentid[x], "'") 
      measurements <- DBI::dbGetQuery(coninfo$con, likelihood.sql)
      
      # field_skill and nofield_skill are alias of max.field.lklh 
      # and max.nofield.lklh 
      c('ml.field' = as.numeric(measurements$field_skill), 
        'ml.nofield' = as.numeric(measurements$nofield_skill), 
        'score.hist' = as.numeric(measurements$new_score))
    })
      
    # calculating mean max likelihood and score from history
    ml.field <- mean(data.frame(do.call(rbind, userhistories))$ml.field)
    ml.nofield <- mean(data.frame(do.call(rbind, userhistories))$ml.nofield)
    score.hist <- mean(data.frame(do.call(rbind, userhistories))$score.hist)

    # read  user polygons that are given as surely-labeled fields
    user.sql <- paste0("SELECT name, geom_clean FROM ",
                        "user_maps where assignment_id = ", "'", x, "' AND NOT ",
                        "category='unsure1' AND NOT category='cloudshadow' 
                       order by name")
    user.polys <- suppressWarnings(DBI::dbGetQuery(coninfo$con, 
                                                     gsub(", geom_clean", 
                                                          "", user.sql)))
    
    # read user polygons for the unsure category
    user.sql.unsure <- paste0("SELECT name, geom_clean FROM ",
                       "user_maps where assignment_id = ", "'", x, "' AND ",
                       "category='unsure1' order by name")
    
    user.polys.unsure <- suppressWarnings(DBI::dbGetQuery(coninfo$con, 
                                                   gsub(", geom_clean", 
                                                        "", user.sql.unsure)))
    
    user.hasfields <- ifelse(nrow(user.polys) > 0, "Y", "N")
    user.unsure.hasfields <- ifelse(nrow(user.polys.unsure) > 0, "Y", "N")
    
    # if user maps have field polygons
    if(user.hasfields == "Y") {
      user.polys <- suppressWarnings(st_read(coninfo$con, query = user.sql, 
                                               geom_column = 'geom_clean'))
        
      # union user polygons
      user.poly <- st_union(user.polys)
        
      # if for F sites, we need to first intersection user maps by grid 
      # to remain those within-grid parts for calculation
      if(qsite == FALSE) {
        user.poly <- suppressWarnings(st_intersection(user.poly, grid.poly))
      }
      
      geometry.user = user.poly
    }
    else {
      # if users do not map field, set geometry as empty polygon
      geometry.user = st_polygon()
    }  
    
    # if user unsure maps have field polygons
    if(user.unsure.hasfields == "Y"){
      user.polys.unsure <- suppressWarnings(st_read(coninfo$con, 
                                                    query = user.sql.unsure, 
                                                    geom_column = 'geom_clean'))
      
      # union user unsure polygons
      user.poly.unsure <- st_union(user.polys.unsure)
      
      # if for F sites, we need to first intersection user maps by grid 
      # to remain those within-grid parts for calculation
      if(qsite == FALSE) {
        user.poly.unsure <- suppressWarnings(st_intersection(user.poly.unsure, 
                                                             grid.poly))
      }
      
      geometry.user.unsure = user.poly.unsure
    }
    else {
      # if users do not map field, set geometry as empty polygon
      geometry.user.unsure = st_polygon()
    } 
    
    # we give 0.5 as posterior probability to unsure, meaning that the user
    # thinks it has only 50% to be a field
    # bayes.poly will consist two sf rows, the first is that the surely-labeled
    # fields, and the second is that unsure fields
    bayes.poly <- st_sf('posterior.field' = c(1, 0.5), 
                        'max.field.lklh' = c(ml.field, ml.field) , 
                        'max.nofield.lklh' = c(ml.nofield, ml.nofield) , 
                        'prior'= c(score.hist, score.hist), 
                        geometry = st_sfc(geometry.user, geometry.user.unsure))
    
    # set crs
    st_crs(bayes.poly) <- gcsstr
    
    bayes.poly
   
  })
  
  bayes.polys <- do.call(rbind, bayes.polys)
  
  if (nrow(bayes.polys) == 0) {
    stop("There is no any valid assignment for creating consensus maps")
  }
  
  # count the number of user maps that has field polygons
  count.hasuserpolymap <- length(which(st_is_empty(bayes.polys[, "geometry"]) ==
                                         FALSE))
  
  # if no any user map polygons for this grid or if for qsite, 
  # use the grid extent as the raster extent
  if ((qsite == FALSE) || (count.hasuserpolymap == 0)) {
    rasterextent <- grid.poly
  }
  # for Q sites, use the maximum combined boundary of all polygons and master grid
  # as the raster extent
  else {
    bb.grid <- st_bbox(grid.poly)
    bb.polys <- st_bbox(st_union(bayes.polys))
    new.bbbox <- st_bbox(c(xmin = min(bb.polys$xmin,bb.grid$xmin), 
                           xmax = max(bb.polys$xmax,bb.grid$xmax), 
                           ymax = max(bb.polys$ymax,bb.grid$ymax), 
                           ymin = min(bb.polys$ymin,bb.grid$ymin)), 
                         crs = gcsstr)
    rasterextent <- st_sf(geom = st_as_sfc(new.bbbox))
  }
  
  # Threshold here for determine field pixels in heat maps (not threshold for risk
  # pixels )
  bayesoutput <- bayes_model_averaging(bayes.polys = bayes.polys,
                                       rasterextent = rasterextent,
                                       threshold = 0.5)
  
  riskpixelpercentage <- ncell(bayesoutput$riskmap
                                   [bayesoutput$riskmap > riskpixelthres]) /
                             (nrow(bayesoutput$riskmap) * 
                                ncol(bayesoutput$riskmap))
  # need add riskpixelpercentage column into kml_data tables
  # insert risk pixel percentage into kml_data table
  # UPDATE Student SET NAME = 'PRATIK', ADDRESS = 'SIKKIM' WHERE ROLL_NO = 1;
  risk.sql <- paste0("update kml_data set consensus_conflict = '", 
                    riskpixelpercentage, "' where name = '", kmlid, "'")
  dbSendQuery(coninfo$con, risk.sql) 
  
  ###################### S3 bucket output ###############
  xy_tabs <- tbl(coninfo$con, "master_grid") %>% 
                          filter(name == kmlid) %>% 
                          dplyr::select(x, y) %>% collect()
  
  
  rowcol <- rowcol_from_xy(xy_tabs$x, xy_tabs$y, offset = -1)
  
  S3BucketDir.sql <- paste0("SELECT value ",
                                  "FROM configuration WHERE ",
                                  "key='S3BucketDir'")

  s3.dst <- dbFetch(DBI::dbSendQuery(coninfo$con, S3BucketDir.sql))$value
  # read  user polygons that are not unsure
  provider.sql <- paste0("SELECT provider FROM",
                     " scene_data WHERE name = '", kmlid, "'")
  
  # provide could be 'planet' or 'wv2'
  provider <- suppressWarnings(DBI::dbGetQuery(coninfo$con, 
                                               provider.sql))
  
  
  s3.dst.train <- paste0(s3.dst, provider, '/', kml.usage, '/')
  
  bucketname <- unlist(strsplit(s3.dst, '/'))[1]
  
  # s3.dst <- paste0("activemapper/sources/train/")  
  s3.filename <- paste0(kmlid, '_', rowcol[1,'row'], '_', rowcol[1,'col'])
  s3_upload(coninfo$dinfo["project.root"], bucketname, 
            bayesoutput$labelmap, 
            substr(s3.dst.train, nchar(bucketname) + 1, nchar(s3.dst.train)),
            s3.filename)
  
  if(output.riskmap == TRUE) { 
    s3.filename <- paste(kmlid + "_risk")
    s3_upload(coninfo$dinfo["project.root"], bucketname, bayesoutput$riskmap, 
              s3.dst, s3.filename)
  }
   
  #######################################################
  
  garbage <- DBI::dbDisconnect(coninfo$con)
  
  return(riskpixelpercentage)
}