#! /usr/bin/Rscript

## packages
library(data.table)
library(raster)
library(DBI)
library(dplyr) # replace RPostgreSQL
library(dbplyr) 

# Hardcoded 
test.root <- "N"
fname <- "KMLgenerate"  # KMLgenerate
kml_type <- "N"  # Type of KML (N for non-QAQC)
diam <- 0.005 / 2 # half of the pixel resolution
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
alt.root <- NULL 
host <- NULL  # host <- "crowdmapper.org"
db.tester.name <- NULL  # db.tester.name <- "lestes"

# variables
# data(pgupw)
suppressMessages(library(rmapaccuracy)) # have to load this to get connection
coninfo <- mapper_connect(user = pgupw$user, password = pgupw$password,
                          db.tester.name = db.tester.name, 
                          alt.root = alt.root, host = host)
## File paths
log_file_path <- paste0(coninfo$dinfo["project.root"], "/log/")

## Record daemon start time
pstart_string <- paste0("KMLgenerate: Daemon starting up at ", 
                        format(Sys.time(), "%a %b %e %H:%M:%S %Z %Y"))

## Initialize csv to log database error message
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
  kml_polling_interval <- as.numeric(
    (tbl(coninfo$con, "configuration") %>% 
       filter(key == 'KMLPollingInterval') %>% collect())$value)
        
        # Target batch size: should be at least 500
  kml_batch_size <- as.numeric(
    (tbl(coninfo$con, "configuration") %>% filter(key == 'NKMLBatchSize') %>%
       collect())$value)
        
  # how many unmapped kmls should there be, at a minimum
  min_avail_kml <- as.numeric(
    (tbl(coninfo$con, "configuration") %>% 
       filter(key == 'MinAvailNKMLTarget') %>% collect())$value)        
        
  # how many unmapped kmls are there? 
  avail_kml_count <- as.numeric(
    tbl(coninfo$con, "kml_data") %>% 
      anti_join(
        (tbl(coninfo$con, "hit_data") %>% 
           left_join(tbl(coninfo$con, "kml_data"), by = "name") %>%
           filter(is.na(delete_time))), by = "name") %>%
      filter((kml_type == 'N') & (mapped_count == 0)) %>%
      summarise(n = n()) %>%collect())
  
  first_avail_line <- as.numeric(
    (tbl(coninfo$con, "system_data") %>% filter(key == 'firstAvailLine') %>%
       collect())$value)
        
  # Select new grid cells for conversion to kmls if N unmapped < min_avail_kml
  start_time <- Sys.time()
  if(avail_kml_count < min_avail_kml) {  
                
    # Step 1. Read the database table in order
    # Already finish the weighted sampling in create_master_grid
    xy_tabs <- coninfo$con %>% tbl("master_grid") %>%
      filter((gid >= first_avail_line) & 
               (gid <= first_avail_line + kml_batch_size - 1)) %>%
      select(id, name, avail) %>%
      head(kml_batch_size) %>% collect()
    xy_tabs <- data.table(xy_tabs)  # convert to data.table (not needed???)

    # Step 2. Update database tables
    # Update kml_data to show new names added and their kml_type
    # Quit saving the 'fwts'
    kml_new <- data.frame(name = xy_tabs$name, 
                          kml_type = rep(kml_type, nrow(xy_tabs)))
    db_insert_into(coninfo$con, table = "kml_data", values = kml_new)
                
    # Update master to show grid is no longer available for selecting/writing
    sqlrt2 <- paste0(" (", paste0("'", xy_tabs$name, "'", collapse = ","), ")")
    sql <- paste("UPDATE master_grid SET avail='F' where name in", sqlrt2)        
    dbExecute(coninfo$con, sql)
                
    # Update master_grid_counter
    count_tab <- tbl(coninfo$con, "master_grid_counter") %>% arrange(block) %>% 
      collect()
    count_tab <- data.table(count_tab, key = "counter")
    if(count_tab[, sum(counter)] == 0) {
      active_block <- count_tab[1, ]
    } else {
      active_block <- count_tab[counter < max(nrows), .SD[1]]
    }
    newcount <- active_block[, counter] + kml_batch_size
    sql <- paste0("UPDATE master_grid_counter SET counter=", newcount, 
                  " WHERE block=", active_block[, block])
    dbExecute(coninfo$con, sql)
                
    # Update the first_avail_line in configuration
    newline <- first_avail_line + kml_batch_size
    sql <- paste0("UPDATE system_data SET value=", newline,
                  " WHERE key='firstAvailLine'")
    dbExecute(coninfo$con, sql)
    
    # Step 3. Database (crude) error handling
    exception <- dbGetException(coninfo$con)  # update exceptions
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
    write(as.character(kml_new$name), file = logfname, 
          append = TRUE, ncolumns = 8)
    write(log_timestamp[2], file = logfname, append = TRUE)
    write("", file = logfname, append = TRUE)
  } 
  Sys.sleep(kml_polling_interval)
}
