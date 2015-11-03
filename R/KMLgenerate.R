#! /usr/bin/Rscript
# KMLgenerate.R (updated version)

####################### 
# Hardcoded 
test.root <- "N"
prjsrid   <- 102022  # EPSG identifier for equal area project
fname <- "KMLgenerate"  # KMLgenerate 
kml_type <- "N"  # Type of KML (N for non-QAQC)
diam <- 500
######################

library(RPostgreSQL)
library(rmapaccuracy)
library(data.table)

# Determine working directory and database
dinfo <- getDBName()  # pull working environment

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")
#dbListConnections(drv); dbGetInfo(drv); summary(con)

# CRS (coordinate reference systems)
sql <- paste0("select proj4text from spatial_ref_sys where srid=", prjsrid)
prjstr <- dbGetQuery(con, sql)$proj4text
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

# File paths
kml_file_path <- paste0(dinfo["project.root"], "/kmls/")
log_file_path <- paste0(dinfo["project.root"], "/log/")

# Write out pid to file and record daemon start time
pid <- Sys.getpid()
pidfile <- paste0(log_file_path, fname, ".pid")
write(pid, file = pidfile)  # Write out pid to new file, overwriting if exists
pstart_string <- paste0("KMLgenerate: Daemon starting up at ", 
                        format(Sys.time(), "%a %b %e %H:%M:%S %Z %Y"), 
                        " (pid ", pid, ")")

# Initialize csv to log database error message
log_hdr <- rbind("Error messages from KMLgenerate.R", 
                 "Time errcode errmessage",
                 "#####################################################")
### Possible conflict
dberrfname <- paste0(log_file_path, "KMLgenerate_dbase_error.log") 
if(!file.exists(dberrfname)) {
  write.table(log_hdr, file = dberrfname, sep = "", col.names = FALSE, 
              row.names = FALSE, quote = FALSE)
}
options(digit.secs = 4)  # Display milliseconds for time stamps 

# Initialize Rlog file to record daemon start time, which kml ids written & when
rlog_hdr <- rbind("Log of KMLgenerate.R start, KML ids written & times", 
                  "####################################################")
logfname <- paste0(log_file_path, fname, ".log")  # Log file name
if(!file.exists(logfname))  write(rlog_hdr, file = logfname)
# Write out daemon start stamp
write(pstart_string, file = logfname, append = TRUE)  

repeat {
  
  # Query polling interval
  sql <- "select value from configuration where key = 'KMLPollingInterval'"
  kml_polling_interval <- as.numeric(dbGetQuery(con, sql)$value)
  
  # Target batch size: should be at least 500
  sql <- "select value from configuration where key = 'NKMLBatchSize'"
  kml_batch_size <- as.numeric(dbGetQuery(con, sql)$value)
  
  # how many unmapped kmls should there be, at a minimum
  sql <- "select value from configuration where key = 'MinAvailNKMLTarget'"
  min_avail_kml <- as.numeric(dbGetQuery(con, sql)$value)
  
  # how many unmapped kmls are there? 
  sql <- paste("select count(*) from kml_data k where not exists",  
               "(select true from hit_data h where h.name = k.name and", 
               "delete_time is null) and kml_type = 'N' and mapped_count = 0")
  avail_kml_count <- dbGetQuery(con, sql)$count
  
  #write(paste(avail.kml.count, "KMLs are unused"), file = logfname, append = TRUE)
  
  # Select new grid cells for conversion to kmls if N unmapped < min_avail_kml
  start_time <- Sys.time()
  if(avail_kml_count < min_avail_kml) {  
    
    # Step 1. Poll the database to see which grid IDs are still available
    sql <- "select name, x, y, fwts from master_grid where avail = 'T'"
    xy_tab <- data.table(dbGetQuery(con, sql))
    
    # Step 2. Draw weighted random sample = min.kml.batch
    # Just an ordinary random sample to select cells, because the weighted
    # draw was already made in creating master_grid
    set.seed(2)
    xy_tab <- xy_tab[{name %in% sample(name, size = kml_batch_size, 
                                       replace = FALSE)}]
      
    # Step 3. Convert them to polygons
    gpols <- spTransform(point_to_gridpoly(xy = as.data.frame(xy_tab), 
                                           w = diam, CRSobj = CRS(prjstr)), 
                         CRSobj = CRS(gcs))
        
    # And convert them to kmls 
    for(i in 1:nrow(gpols)) {
      kml_name <- paste0(dinfo["project.root"], "/kmls/", gpols$name[i], ".kml")
      rgdal::writeOGR(gpols[i, ], dsn = kml_name, layer = gpols$name[i], 
                      driver = "KML", overwrite = TRUE)
    }
    
    # Step 4. Update database tables
    # Update kml_data to show new names added and their kml_type
    sqlrt <-  paste0("('", gpols$name, "', ", "'", kml_type,"','", gpols$fwts,"')", collapse = ",")
    sql <- paste("insert into kml_data (name, kml_type, fwts) values ", sqlrt)
    ret <- dbSendQuery(con, sql)
    
    # Update master to show grid is no longer available for selecting/writing
    sqlrt2 <- paste0(" (", paste0("'", gpols$name, "'", collapse = ","), ")")
    sql <- paste("UPDATE master_grid SET avail='F' where name in", sqlrt2)        
    ret2 <- dbSendQuery(con, sql)
    
    # Update master_grid_counter
    sql <- paste("SELECT * from master_grid_counter ORDER BY block")
    count_tab <- data.table(dbGetQuery(con, sql), key = "block")
    if(count_tab[, sum(counter)] == 0) {
      active_block <- count_tab[1, ]
    } else {
      active_block <- count_tab[counter < max(nrows), .SD[1]]
    }
    newcount <- active_block[, counter] + 500
    sql <- paste0("UPDATE master_grid_counter SET counter=", newcount, 
                  " WHERE block=", active_block[, block])
    ret3 <- dbSendQuery(con, sql)
    
    # Step 6. Database (crude) error handling
    exception <- dbGetException(con)  # update exceptions
    if(exception$errorNum != 0) {
      print("Error updating master_grid")  
      errors <- paste(gsub("EDT", "", Sys.time()), "  ", 
                      paste(exception, collapse = "    "))
      write(errors, file = dberrfname, append = TRUE)
      quit(status = exception$errorNum, save = "no")
    }
  }
  end_time <- Sys.time()
  
  # Write out kmlID log
  log_timestamp <- c(format(start_time, "%a %b %d %X %Y %Z"), 
                     format(end_time, "%a %b %d %X %Y %Z"))
  if(avail_kml_count < min_avail_kml) {
    write(log_timestamp[1], file = logfname, append = TRUE)
    write(gpols$name, file = logfname, append = TRUE, ncolumns = 8)
    write(log_timestamp[2], file = logfname, append = TRUE)
    write("", file = logfname, append = TRUE)
  } 
  Sys.sleep(kml_polling_interval)
}
