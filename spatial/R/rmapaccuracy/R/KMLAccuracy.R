#' Main function for running worker accuracy assessment
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
#' @import sp
#' @import RPostgreSQL
#' @importFrom DBI dbDriver
#' @importFrom rgeos gUnaryUnion gIntersection gDifference gArea
#' @export
KMLAccuracy <- function(mtype, kmlid, assignmentid, tryid, 
                        prjsrid, count.err.wt, in.err.wt, out.err.wt, 
                        err.switch, comments, write.err.db, draw.maps, test,  
                        test.root, user, password) {
  
  dinfo <- getDBName()  # pull working environment

  # Paths and connections
  drv <- dbDriver("PostgreSQL")
  con <- dbConnect(drv, dbname = dinfo["db.name"], user = user, password = password)
  
  prj.sql <- paste0("select proj4text from spatial_ref_sys where srid=", 
                    prjsrid)
  prjstr <- dbGetQuery(con, prj.sql)$proj4text
  gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
    
  # Collect QAQC fields (if there are any; if not then "N" value will be 
  # returned). This should work for both training and test sites
  qaqc.sql <- paste0("select gid,ST_AsEWKT(geom_clean),ST_AsEWKT(geom)", 
                     " from qaqcfields where name=", "'", kmlid, "'")
  qaqc.geom.tab <- dbGetQuery(con, qaqc.sql)
  qaqc.hasfields <- ifelse(nrow(qaqc.geom.tab) > 0, "Y", "N") 
  if(qaqc.hasfields == "Y") {
    qaqc.geom.tab[, 2] <- gsub("^SRID=*.*;", "", qaqc.geom.tab[, 2])
    qaqc.polys <- polyFromWkt(geom.tab = qaqc.geom.tab, crs = prjstr)
    qaqc.nfields <- nrow(qaqc.polys)
    qaqc.polys <- gBuffer(qaqc.polys, width = 0)
    qaqc.poly <- gUnaryUnion(qaqc.polys)    
  } 
  
  # Read in user data
  if(mtype == "tr") {  # Training case
    user.sql <- paste0("select name,ST_AsEWKT(geom_clean),ST_AsEWKT(geom),try",
                       " from qual_user_maps where ",  assignmentidtype, "='", 
                       assignmentid, "'", " and try='",  tryid, 
                       "' order by name")
  } else if(mtype == "qa") {  # Test case
    user.sql <- paste0("select name,ST_AsEWKT(geom_clean),ST_AsEWKT(geom) from", 
                       " user_maps where assignment_id=", "'", assignmentid, 
                       "'", " order by name")  
  }
  user.geom.tab <- dbGetQuery(con, user.sql)
  user.geom.tab <- user.geom.tab[grep(kmlid, user.geom.tab$name), ]  
  user.hasfields <- ifelse(nrow(user.geom.tab) > 0, "Y", "N") 
  if(user.hasfields == "Y") {  # Read in user fields if there are any
    if(any(is.na(user.geom.tab[, 2]))) {  # invoke cleaning algorithm 
       user.geom.tab[, 3] <- gsub("^SRID=*.*;", "", user.geom.tab[, 3])
       user.poly.list <- cleanTempPolyFromWKT(geom.tab=user.geom.tab[, c(1, 3)], 
                                              crs = gcs)
       user.nfields <- user.poly.list[[2]]  #  Record n distinct fields
       user.poly <- gUnaryUnion(spTransform(user.poly.list[[1]], 
                                            CRSobj = CRS(prjstr)))  
      } else if(all(!is.na(user.geom.tab[, 2]))) { 
        user.geom.tab[, 2] <- gsub("^SRID=*.*;", "", user.geom.tab[, 2])
        user.polys <- polyFromWkt(geom.tab = user.geom.tab, crs = gcs)
        user.nfields <- nrow(user.polys)
        user.poly <- gUnaryUnion(spTransform(user.polys, CRSobj = CRS(prjstr)))
      }
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
    if(mtype == "tr") {  # Training case
      grid.sql <- paste0("SELECT id,ST_AsEWKT(geom) from qual_sites where name=", 
                         "'", kmlid, "'")
    } else if(mtype == "qa") {  # QAQC case
      grid.sql <- paste0("SELECT id,ST_AsEWKT(geom) from newqaqc_sites where",
                        " name=", "'", kmlid, "'")
    }
    grid.geom.tab <-dbGetQuery(con, grid.sql)
    grid.geom.tab[, 2] <- gsub("^SRID=*.*;", "", grid.geom.tab[, 2])
    grid.poly <- polyFromWkt(geom.tab = grid.geom.tab, crs = prjstr)
  }
  
  # Case 2: A null qaqc site but user mapped field(s)
  if((qaqc.hasfields == "N") & (user.hasfields == "Y")) {
    if(comments == "T") print("No QAQC fields, but there are User fields") 
    
    # Accuracy measures
    count.error <- 0  # zero if QAQC has no fields but user maps even 1 field
    
    # Mapped area differences inside the target grid cell
    user.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = user.poly, 
                                  byid = TRUE)  
    inres <- mapError(maps = user.poly.in, truth = NULL, region = grid.poly)
    
    # Secondary metric - Sensitivity of results outside of kml grid
    user.poly.out <- gDifference(spgeom1 = user.poly, spgeom2 = grid.poly, 
                                 byid = TRUE)
    if(is.null(user.poly.out)) {
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
      qaqc.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = qaqc.poly, 
                                    byid = TRUE)  
      qaqc.poly.out <- gDifference(spgeom1 = qaqc.poly, spgeom2 = grid.poly, 
                                   byid = TRUE)
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
      user.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = user.poly, 
                                    byid = TRUE)
      qaqc.poly.in <- gIntersection(spgeom1 = grid.poly, spgeom2 = qaqc.poly, 
                                    byid = TRUE)
      user.poly.out <- gDifference(spgeom1 = user.poly, spgeom2 = grid.poly, 
                                   byid = TRUE)
      qaqc.poly.out <- gDifference(spgeom1 = qaqc.poly, spgeom2 = grid.poly, 
                                   byid = TRUE)
      inres <- mapError(maps = user.poly.in, truth = qaqc.poly.in, 
                        region = grid.poly)  # Error metric
      
      # Secondary metric - Sensitivity of results outside of kml grid
      if(is.null(user.poly.out) & is.null(qaqc.poly.out)) {
        if(comments == "T") print("No QAQC or User fields outside of grid")
        out.error <- 1  
      } else if(!is.null(user.poly.out) & !is.null(qaqc.poly.out)) {
        if(comments == "T") print("Both QAQC and User fields outside of grid")
        tpo <- gIntersection(spgeom1 = qaqc.poly.out, spgeom2 = user.poly.out)  
        fno <- gDifference(spgeom1 = qaqc.poly.out, spgeom2 = user.poly.out)  
        tflisto <- c("tpo", "fno")  
        areaso <- sapply(tflisto, function(x) {
          ifelse(!is.null(get(x)) & is.object(get(x)), gArea(get(x)), 0)
        })
        out.error <- areaso[1] / sum(areaso)
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
      err.out <- c("total_error" = err, "count_error" = count.error, 
                   "out_error" = out.error, 
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
      error.sql <- paste0("insert into qual_error_data(training_id, name,", 
                          " score, error1, error2, error3, error4, try, tss)", 
                          " values ('", assignmentid, "', ", "'", kmlid, "', ", 
                          paste(err.out, collapse = ", "), ", ", tryid, ", ", 
                          tss.err, ")")  # Write try error data
    }  
    ret <- dbSendQuery(con, error.sql)
  }
    
  # Map results according to error class
  if(draw.maps == "T") {
    
    if(exists("grid.poly")) bbr1 <- sp::bbox(grid.poly)
    if(exists("qaqc.poly")) bbr2 <- sp::bbox(qaqc.poly)
    if(exists("user.poly")) bbr3 <- sp::bbox(user.poly)
    
    cx <- 1.5 
    lbbrls <- ls(pattern = "^bbr")
    if(length(lbbrls) > 0) {
      xr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[1, ]))
      yr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[2, ]))
      vals <- rbind(xr, yr)
      
      if(exists("grid.poly")) {
        tm <- format(Sys.time(), "%Y%m%d%H%M%OS2")  
        pngname <- paste0(dinfo["project.root"], "/spatial/R/Error_records/", 
                          kmlid, "_", assignmentid, "_", tm, ".png")
        png(pngname, height = 700, width = 700, antialias = "none")
        plot(grid.poly, xlim = vals[1, ], ylim = vals[2, ])
        objchk <- sapply(2:5, function(x) is.object(inres[[x]]))
        mpi <- names(err.out)
        plotpos <- c(0.15, 0.4, 0.65, 0.90)
        cols <- c("green4", "red4", "blue4", "grey30")
        for(i in 1:4) {
          if(objchk[i] == "TRUE") plot(inres[[i + 1]], add = T, col = cols[i])
          mtext(round(err.out[i], 3), side = 3, line = -1, adj = plotpos[i], 
                cex = cx)
          mtext(mpi[i], side = 3, line = 0.5, adj = plotpos[i], cex = cx)
          if(exists("user.poly.out")) {
            if(!is.null(user.poly.out)) {
              plot(user.poly.out, add = T, col = "grey")
            }
          }
          if(exists("qaqc.poly.out")) {
            if(!is.null(qaqc.poly.out)) {
              plot(qaqc.poly.out, add = T, col = "pink")
            }
          }
          if(exists("tpo")) {
            if(is.object(tpo)) plot(tpo, col = "green1", add = TRUE)
          }
          if(exists("fno")) {
            if(is.object(tpo)) plot(fno, col = "blue1", add = TRUE)
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

