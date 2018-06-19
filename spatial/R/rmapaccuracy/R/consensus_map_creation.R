#' Control the output of label maps, risk maps, and heat maps 
#' @param kmlid 
#' @param min_mappedcount the minimum approved assignment count
#' @param scorethres the threshold to select valid assignment
#' @param riskthres the threshold to select 'risk' pixels
#' @param user User name for database connection
#' @param password Password for database connection
#' @param db.tester.name User name for testing (default NULL)
#' @param alt.root Alternative location for writing out maps (default NULL)
#' @param host NULL or "crowdmapper.org", if testing from remote location
#' @import RPostgreSQL
#' @importFrom  DBI dbDriver
#' @import dplyr
#' @import sf
#' @return Sticks conflict/risk percentage pixels into database (kml_data) and
#' (pending) writes rasters to S3 bucket
#' @export
consensus_map_creation <- function(kmlid, min_mappedcount, scorethres, 
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
 
  if (mappedcount < min_mappedcount) {
    stop("there is not enough approved assignment for creating consensus maps")
  }

  
  # query assignmentid flagged as 'approved'
  assignment.sql <- paste0("select assignment_id from assignment_data", 
                           " where hit_id ='", hitid, 
                           "' and status = 'Approved'", 
                           " order by assignment_id")  
  
  assignmentid <- (DBI::dbGetQuery(coninfo$con, assignment.sql))$assignment_id
  
  # read grid polygon
  xy_tabs <- data.table(tbl(coninfo$con, "master_grid") %>% 
                          filter(name == kmlid) %>% 
                          dplyr::select(x, y, name) %>% collect())
  # read grid geometry, and keep gcs
  grid.poly <- point_to_gridpoly(xy = xy_tabs, w = diam, NewCRSobj = gcsstr, 
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
    workerid <- "88"
    histassignid.sql <- paste0("select assignment_id from", 
                               " assignment_data where worker_id = '", 
                               workerid, "'",
                               " and (status = 'Approved' OR status = ",
                               "'Rejected') and score IS NOT NULL")
    historyassignmentid <- ((DBI::dbGetQuery(coninfo$con, 
                                             histassignid.sql))$assignment_id)
      
    # read all valid likelihood and score from history assignments
    userhistories <- lapply(c(1:length(historyassignmentid)), function(x) {
      ################### test lines##############################
      # likelihood.sql <- paste0("select new_score from new_error_data", 
      #                            " where assignment_id  = '", 
      #                            historyassignmentid[x], "'") 
      # max_lklh_field <- as.numeric((DBI::dbGetQuery(coninfo$con, likelihood.sql))
      #                          $new_score) 
      # max_lklh_nofield <- as.numeric((DBI::dbGetQuery(coninfo$con, likelihood.sql))
      #                            $new_score) 
      # score_history <- as.numeric((DBI::dbGetQuery(coninfo$con, likelihood.sql))
      #                             $new_score) 
      # c('lklh_field' = max_lklh_field, 'lklh_nofield' = max_lklh_nofield, 
      #                                'score_history' = score_history)
      ################### test lines###############################
                                         
      ################### official lines###########################
      # need add field_skill and nofield_skill columns to new_error_data tables
      likelihood.sql <- paste0("select new_score, field_skill, nofield_skill",
                               " from new_error_data  where assignment_id  = '", 
                               historyassignmentid[x], "'") 
      measurements <- DBI::dbGetQuery(coninfo$con, likelihood.sql)
      # field_skill and nofield_skill are alias of max_field_lklh 
      # and max_nofield_lklh 
      c('ml_field' = as.numeric(measurements$field_skill), 
        'ml_nofield' = as.numeric(measurements$nofield_skill), 
        'score_hist' = as.numeric(measurements$new_score))
      ################### official lines###########################
    })
      
    # calculating mean max likelihood and score from history
    ml_field <- mean(data.frame(do.call(rbind, userhistories))$ml_field)
    ml_nofield <- mean(data.frame(do.call(rbind, userhistories))$ml_nofield)
    score_hist <- mean(data.frame(do.call(rbind, userhistories))$score_hist)
    # if the user score is larger than the required 
    # score threshold, then output user.poly and likelihood
    if(score_hist > scorethres) {
      # test if user fields exist
      user.sql <- paste0("select geom_clean from",
                         " user_maps where assignment_id = ", "'", x,
                         "'", " order by name")
      user.polys <- suppressWarnings(DBI::dbGetQuery(coninfo$con, 
                                                     gsub(", geom_clean", 
                                                          "", user.sql)))
      user.hasfields <- ifelse(nrow(user.polys) > 0, "Y", "N")
      # if user maps have field polygons
      if(user.hasfields == "Y") {
        user.polys <- suppressWarnings(st_read(coninfo$con, query = user.sql, 
                                               geom_column = 'geom_clean'))
        
        # union user polygons
        user.poly <- st_union(user.polys)
        
        # if for N or F sites, we need to first intersection user maps by grid 
        # to remain those within-grid parts for calculation
        if(qsite == FALSE) {
          user.poly <- suppressWarnings(st_intersection(user.poly, grid.poly))
        }
        bayes.poly <- st_sf('posterior_field' = 1, 'posterior_nofield' = 1,
                            'max_field_lklh' = ml_field , 
                            'max_nofield_lklh' = ml_nofield , 
                            'prior'= score, geometry = st_sfc(user.poly))
        
        # set crs
        st_crs(bayes.poly) <- gcsstr
      }
      else {
        # if users do not map field, set geometry as empty multipolygon
        bayes.poly <- st_sf('posterior_field' = 1, 'posterior_nofield' = 1,
                            'max_field_lklh' = ml_field, 
                            'max_nofield_lklh' = ml_nofield, 
                            'prior'= score, 
                            geometry = st_sfc(st_multipolygon()))
        st_crs(bayes.poly) <- gcsstr
      }
      bayes.poly
    }
  })
  
  bayes.polys <- do.call(rbind, bayes.polys)
  
  if (nrow(bayes.polys) == 0) {
    stop("There is not enough valid assignments (> minimum score)")
  }
  
  # count the number of user maps that has field polygons
  count_hasuserpolymap <- length(which(st_is_empty(bayes.polys[, "geometry"]) ==
                                         FALSE))
  
  # if no any user map polygons for this grid or if for qsite, 
  # use the grid extent as the raster extent
  if ((qsite == FALSE) || (count_hasuserpolymap == 0)) {
    rasterextent <- grid.poly
  }
  # for Q sites, use the maximum combined boundary of all polygons and master grid
  # as the raster extent
  else {
    bb_grid <- st_bbox(grid.poly)
    bb_polys <- st_bbox(st_union(bayes.polys))
    new_bbbox <- st_bbox(c(xmin = min(bb_polys$xmin,bb_grid$xmin), 
                           xmax = max(bb_polys$xmax,bb_grid$xmax), 
                           ymax = max(bb_polys$ymax,bb_grid$ymax), 
                           ymin = min(bb_polys$ymin,bb_grid$ymin)), 
                         crs = gcsstr)
    rasterextent <- st_sf(geom = st_as_sfc(new_bbbox))
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
  risk.sql <- paste0("insert into kml_data (consensus_conflict)", 
                     " values ('", riskpixelpercentage, "')")
  dbSendQuery(coninfo$con, risk.sql) # will be changed to official lines
  
  ###################### S3 bucket output ###############
  # unfinished
  #######################################################
  
  garbage <- dbDisconnect(coninfo$con)
}