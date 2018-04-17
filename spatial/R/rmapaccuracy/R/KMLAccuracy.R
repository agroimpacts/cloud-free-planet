#' Main function for running worker accuracy assessment
#' @param diam diameter for master grids
#' @param prjsrid EPSG identifier for projected coordinate system
#' @param count.err.wt Weighting given to field count error
#' @param in.err.wt Weighting for in grid map discrepancy
#' @param out.err.wt Weighting for out of grid map discrepancy
#' @param err.switch in grid error metric: 1 = overall accuracy; 2 = TSS
#' @param comments For testing, can turn off (F) or on (T) print statements
#' @param write.err.db Write error metrics into error_data table ("T" or "F") 
#' @param draw.maps Draw maps showing output error components ("T" or "F") 
#' @param test "Y" or "N" for offline testing mode (see Details)
#' @param test.root "Y" or "N" for testing current working location
#' @param user User name for database connection
#' @param password Password for database connection
#' @details For the test argument, it can be set to "Y" if one wants to test a 
#' given only a single kmlid. In this case, the function code will pull the 
#' entire assignment_data and hit_data tables from the database to find the 
#' right assignment ids to test. This option must be set to "N" when in  
#' production. test.root allows one to simply the run the function to see if it 
#' is located in the correct working environment.
#' @import RPostgreSQL
#' @importFrom  DBI dbDriver
#' @import dplyr
#' @import sf
#' @export
KMLAccuracy <- function(mtype, kmlid, assignmentid, tryid, diam,
                        prjsrid, count.err.wt, in.err.wt, out.err.wt, 
                        err.switch, comments, write.err.db, draw.maps, test,  
                        test.root, user, password) {
  
  dinfo <- getDBName()  # pull working environment

  # Paths and connections
  con <- DBI::dbConnect(RPostgreSQL::PostgreSQL(), dbname = dinfo["db.name"],   
                        user = user, password = password)

  prjstr <- as.character(tbl(con, "spatial_ref_sys") %>% 
                           filter(srid == prjsrid) %>% 
                           select(proj4text) %>% collect())
  
  gcsstr <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
    
  # Collect QAQC fields (if there are any; if not then "N" value will be 
  # returned). This should work for both training and test sites
  qaqc.sql <- paste0("select gid, geom_clean",
                     " from qaqcfields where name=", "'", kmlid, "'")
  qaqc.polys <- suppressWarnings(st_read_db(con, query = qaqc.sql, 
                                            geom_column = 'geom_clean'))
  qaqc.hasfields <- ifelse(nrow(qaqc.polys) > 0, "Y", "N") 
  if(qaqc.hasfields == "Y") {
    qaqc.nfields <- nrow(qaqc.polys)
    qaqc.polys <- st_transform(qaqc.polys,crs=prjstr)
    qaqc.polys <- st_buffer(qaqc.polys, 0)
    qaqc.poly <- st_union(qaqc.polys) 
  } 

  # Read in user data
  if(mtype == "tr") {  # Training case
    user.sql <- paste0("select name, geom_clean, geom, try",
                       " from qual_user_maps where assignment_id=",  "'", 
                       assignmentid, "'", " and try='",  tryid, 
                       "' order by name")
  } else if(mtype == "qa") {  # Test case
    user.sql <- paste0("select name, geom_clean, geom from",
                       " user_maps where assignment_id=", "'", assignmentid,
                       "'", " order by name")
  }
  user.polys <- suppressWarnings(st_read_db(con, query = user.sql, 
                                            geom_column = 'geom_clean'))
  user.hasfields <- ifelse(nrow(user.polys) > 0, "Y", "N") 
  if(user.hasfields == "Y") {  # Read in user fields if there are any
    # if(any(st_is_empty(user.polys))) {  # invoke cleaning algorithm
    #   unfixedsfc <- lapply(as.vector(user.polys$geom), function(vec) {
    #     structure(vec, class = "wkb")
    #   })
    #   unfixedsfc <- st_as_sfc(unfixedsfc, EWKB = TRUE)
    #   user.polysclean <- cleanTempPolyFromWKT(unfixedsfc = unfixedsfc, 
    #                                           crs = gcs)
    #   user.nfields <- nrow(user.polysclean)  #  Record n distinct fields
    #   # transform user polygons into pcs for calculation
    #   user.poly <- st_union(st_transform(user.polysclean,crs = prjstr)) 
    # } else if(all(!st_is_empty(user.polys))) { 
    #   user.nfields <- nrow(user.polys)
    #   user.poly <- st_union(st_transform(user.polys, crs = prjstr))
    # }  # switched off for now--re-enable if we move back to pprepair
    user.nfields <- nrow(user.polys)
    user.poly <- st_union(st_transform(user.polys, crs = prjstr))
  } 
  
  # Error checks begin
  # Case 1: A null qaqc site recorded as null by the observer; score set to 1
  if((qaqc.hasfields == "N") & (user.hasfields == "N")) {
    if(comments == "T") print("No QAQC or User fields")
    err <- 1
    tss.err <- 1  
    err.out <- c("total_error" = err, "count_error" = 1, "out_error" = 1, 
                 "in_error" = 1, "user_fldcount" = 0)
  } else {
    # Pick up grid cell from qaqc table, for background location, as it will be 
    # needed for the other 3 cases
    xy_tabs <- data.table(tbl(con, "master_grid") %>% filter(name == kmlid) %>% 
                            select(x, y, name) %>% collect())
    
    grid.poly <- point_to_gridpoly(xy = xy_tabs, w = diam, NewCRSobj = prjstr, 
                                   OldCRSobj = gcsstr)
    grid.poly <- st_geometry(grid.poly)  # retain geometry only
  }
  
  # Case 2: A null qaqc site but user mapped field(s)
  if((qaqc.hasfields == "N") & (user.hasfields == "Y")) {
    if(comments == "T") print("No QAQC fields, but there are User fields") 
    
    # Accuracy measures
    count.error <- 0  # zero if QAQC has no fields but user maps even 1 field
    
    # Mapped area differences inside the target grid cell
    user.poly.in <- st_buffer(st_buffer(st_intersection(grid.poly, user.poly),0.00001),-0.00001)  
    inres <- mapError(maps = user.poly.in, truth = NULL, region = grid.poly)
    
    # Secondary metric - Sensitivity of results outside of kml grid
    user.poly.out <- st_buffer(st_buffer(st_difference(user.poly, grid.poly),0.00001),-0.00001)
    if(length(user.poly.out) == 0) {
      out.error <- 1  # If user finds no fields outside of box, gets credit
    } else {  
      out.error <- 0  # If user maps outside of box when no fields exist
    }
    
    # Combine error metric
    err <- count.error * count.err.wt + unname(inres[[1]][err.switch]) * 
      in.err.wt + out.error * out.err.wt 
    tss.err <- inres[[1]][2]
    err.out <- c("total_error" = err, "count_error" = count.error, 
                 "out_error" = out.error, 
                 "in_error" = unname(inres[[1]][err.switch]), 
                 "user_fldcount" = user.nfields)
  }
  
  # Cases 3 & 4
  if(qaqc.hasfields == "Y") {
    
    #  Case 3. QAQC has fields, User has no fields
    if(user.hasfields == "N") {
      if(comments == "T") print("QAQC fields but no User fields")
      # Accuracy measures
      count.error <- 0  # if QAQC has fields but user maps none
      
      # Mapped area differences inside the target grid cell
      qaqc.poly.in <- st_buffer(st_buffer(st_intersection(grid.poly, qaqc.poly),0.00001),-0.00001)  
      qaqc.poly.out <- st_buffer(st_buffer(st_difference(qaqc.poly, grid.poly),0.00001),-0.00001)
      inres <- mapError(maps = NULL, truth = qaqc.poly.in, region = grid.poly)
      
      # Secondary metric - Sensitivity of results outside of kml grid
      out.error <- 0  # 0 if there is neither true positive nor false negative
      
      # Combine error metric
      err <- count.error * count.err.wt + unname(inres[[1]][err.switch]) * 
        in.err.wt + out.error * out.err.wt 
      tss.err <- inres[[1]][2]
      err.out <- c("total_error" = err, "count_error" = count.error, 
                   "out_error" = out.error, 
                   "in_error" = unname(inres[[1]][err.switch]), 
                   "user_fldcount" = 0)
      
      # Case 4. QAQC has fields, User has fields
    } else if(user.hasfields == "Y") {
      if(comments == "T") print("QAQC fields and User fields")
      
      # Accuracy measures
      count.error <- rmapaccuracy::countError(qaqc_rows = qaqc.nfields, 
                                              user_rows = user.nfields) 
      
      # Mapped area differences inside the target grid cell
      user.poly.in <- st_buffer(st_buffer(st_intersection(grid.poly, user.poly),0.00001),-0.00001)  # user maps in cell
      qaqc.poly.in <- st_buffer(st_buffer(st_intersection(grid.poly, qaqc.poly),0.00001),-0.00001)  # q maps in cell
      user.poly.out <- st_buffer(st_buffer(st_difference(user.poly, grid.poly),0.00001),-0.00001)  # user maps outside
      qaqc.poly.out <- st_buffer(st_buffer(st_difference(qaqc.poly, grid.poly),0.00001),-0.00001)  # q maps outside
      
      # Accuracy in the box. 2 possible cases. Normal, user has fields inside 
      # box. Abnormal, for some reason user only mapped outside of box. Inside
      # error collapses to same as Case 3 inside error.
      if(length(user.poly.in) > 0) {  # if user has fields inside
        inres <- mapError(maps = user.poly.in, truth = qaqc.poly.in, 
                          region = grid.poly)  # Error metric
      } else if(length(user.poly.in) == 0) {  
        inres <- mapError(maps = NULL, truth = qaqc.poly.in, region = grid.poly)
      }
      
      # Secondary metric - Sensitivity of results outside of kml grid
      if(length(user.poly.out) == 0 & length(qaqc.poly.out) == 0) {
        if(comments == "T") print("No QAQC or User fields outside of grid")
        out.error <- 1  # perfect if neither u nor q map outside
      } else if(length(user.poly.out) > 0 & length(qaqc.poly.out) > 0) {
        if(comments == "T") print("Both QAQC and User fields outside of grid")
        tpo <- st_intersection(qaqc.poly.out, user.poly.out)  # tp outside
        fno <- st_difference(qaqc.poly.out, user.poly.out)  # fp outside
        tflisto <- c("tpo", "fno")
        areaso <- sapply(tflisto, function(x) {  # calculate tp and fp area
          xo <- get(x)
          ifelse(!is.null(xo) & is.object(xo) & length(xo) > 0, st_area(xo), 0)
        })
        out.error <- areaso[1] / sum(areaso)  # sensitivity 
      } else {
        if(comments == "T") {
          print("Either QAQC or User fields outside of grid, but not both")
        }
        out.error <- 0
      }
      
      # Combine error metric
      err <- count.error * count.err.wt + unname(inres[[1]][err.switch]) * 
        in.err.wt + out.error * out.err.wt 
      tss.err <- inres[[1]][2]
      err.out <- c("total_error" = unname(err), 
                   "count_error" = count.error, 
                   "out_error" = unname(out.error), 
                   "in_error" = unname(inres[[1]][err.switch]), 
                   "user_fldcount" = user.nfields)
    }
  } 
  
  # Insert error component statistics into the database 
  if(write.err.db == "T") {
    if(mtype == "qa") {
      error.sql <- paste0("insert into error_data (assignment_id, score,
                          error1, error2, error3, error4, tss) values ('",
                         assignmentid, "', ", paste(err.out, collapse = ", "),
                         ", ", tss.err,  ")")
    } else if(mtype == "tr") {
      error.sql <- paste0("insert into qual_error_data(assignment_id,",
                          " score, error1, error2, error3, error4, try, tss)",
                          " values ('", assignmentid, "', ",
                          paste(err.out, collapse = ", "), ", ", tryid, ", ",
                          tss.err, ")")  # Write try error data
    }
    ret <- dbSendQuery(con, error.sql)
  }
    
  # Map results according to error class
  if(draw.maps == "T") {
    
  #   error_maps(grid_poly = ifelse(exists("grid.poly"), list(grid.poly), "null")[[1]],
  #              qaqc_poly = ifelse(exists("qaqc.poly"), list(qaqc.poly), "null")[[1]],
  #              user_poly = ifelse(exists("user.poly"), list(user.poly), "null")[[1]],
  #              inres = ifelse(exists("inres"), list(inres), "null")[[1]],  
  #              err_out = err.out, 
  #              user_poly_out = ifelse(exists("user.poly.out"), list(user.poly.out), 
  #                                     "null")[[1]],
  #              qaqc_poly_out = ifelse(exists("qaqc.poly.out"), list(qaqc.poly.out), 
  #                                     "null")[[1]],
  #              tpout = ifelse(exists("tpo"), list(tpo), "null")[[1]],
  #              fnout = ifelse(exists("fno"), list(fno), "null")[[1]],
  #              pngout = FALSE)
  # }
    
    if(exists("grid.poly")) bbr1 <- st_bbox(grid.poly)
    if(exists("qaqc.poly")) bbr2 <- st_bbox(qaqc.poly)
    if(exists("user.poly")) bbr3 <- st_bbox(user.poly)
    
    cx <- 1.5 
    lbbrls <- ls(pattern = "^bbr")
    if(length(lbbrls) > 0) {
      xr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[c(1,3)]))
      yr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[c(2,4)]))
      vals <- rbind(xr, yr)
      
      if(exists("grid.poly")) {
        tm <- format(Sys.time(), "%Y%m%d%H%M%OS2")  
        pngname <- paste0(dinfo["project.root"], "/spatial/R/Error_records/", 
                          kmlid, "_", assignmentid, "_", tm, ".png")
        png(pngname, height = 700, width = 700, antialias = "none")
        plot(st_geometry(grid.poly), xlim = vals[1, ], ylim = vals[2, ])
        objchk <- sapply(2:5, function(x) is.object(inres[[x]]))
        mpi <- names(err.out)
        plotpos <- c(0.15, 0.4, 0.65, 0.90)
        cols <- c("green4", "red4", "blue4", "grey30")
        for(i in 1:4) {
          if(objchk[i] == "TRUE") {
            plot(st_geometry(inres[[i + 1]]), add = TRUE, col = cols[i])
          }
          mtext(round(err.out[i], 3), side = 3, line = -1, adj = plotpos[i], 
                cex = cx)
          mtext(mpi[i], side = 3, line = 0.5, adj = plotpos[i], cex = cx)
          if(exists("user.poly.out")) {
            if(length(user.poly.out) > 0) {
              plot(st_geometry(user.poly.out), add = TRUE, col = "grey")
            }
          }
          if(exists("qaqc.poly.out")) {
            if(length(qaqc.poly.out) > 0) {
              plot(st_geometry(qaqc.poly.out), add = TRUE, col = "pink")
            }
          }
          if(exists("tpo")) {
            if(is.object(tpo) & length(tpo) > 0) {
              plot(tpo, col = "green1", add = TRUE)
            }
          }
          if(exists("fno")) {
            if(is.object(fno) & length(fno) > 0) {
              plot(fno, col = "blue1", add = TRUE)
            }
          }
        }
        mtext(paste0(kmlid, "_", assignmentid), side = 1, cex = cx)
        legend(x = "right", legend = c("TP", "FP", "FN", "TN"), pch = 15, 
               bty = "n", col = cols, pt.cex = 3, cex = cx)
        garbage <- dev.off()  # Suppress dev.off message
      }  
    }
  }
  
  # Clean up a bit (aids with running tests)
  #rmnames <- ls()
  #rm(list = rmnames[!rmnames %in% c("tab", "con", "err.out")])  
  
  # Close connection to prevent too many from being open
  garbage <- dbDisconnect(con)
  
  # Return error metrics
  if(comments == "T") {
    cat(err.out)  # All metrics if comments are on (testing only)
  } else {
    cat(unname(err.out[1]))  # First metric if in production
  }
}

