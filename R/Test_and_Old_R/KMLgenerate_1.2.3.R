#! /usr/bin/R -f 
##############################################################################################################
# Title      : KMLgenerate_1.2.3.R
# Purpose    : KML file generation daemon
# Author     : Dennis McRitchie, Lyndon Estes
# Draws from : KMLgenerate*.R
# Used by    : 
# Notes      : Created 18/10/2012
#              Must be started with: 
#              nohup <path-to-script>/KMLgenerate.R &
#              Dennis: Note I have changed variable naming conventions.  I follow Google Style Guide for R, 
#              which has variable names separated with periods, and functions done in the python style: 
#              e.g. some.variable.name 
#              e.g. someFunctionName
#              Changes from *1.2.R
#              19/10/12: Updated to remove coordinates from kml names, and to remove ".kml" from kml_names
#              22/10/12: Database connections updated to reflect moving of afmap into SouthAfrica
#              26/10/12: Fixed connections and changed error logger to reflect dropping of afmap
#              13/6/12: Updated avail.kml.count to have no sql statement b/c kml_data no longer has hit_id
#                 Ran manually to give some initial non-qaqc kmls to work with
#              20/6/13: Added logging for daemon start time and for pid to be recorded in separate file. 
#                 Daemon start time is recorded in log file that lists NKML ids selected for writing 
##############################################################################################################

library(RPostgreSQL)
library(rgdal)
library(rgeos)

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "SouthAfrica", user = "***REMOVED***", password = "***REMOVED***")
#dbListConnections(drv); dbGetInfo(drv); summary(con)

# Hardcoded data
fname <- "KMLgenerate_1.2.3"  # KMLgenerate version number
country.ID <- "SA"  # Ideally this will be read out of the database, as we expand to other countries
kml.type <- "N"  # Type of KML (N for non-QAQC)

# CRS (coordinate reference systems)
alb <- "+proj=aea +lat_1=-18 +lat_2=-32 +lat_0=0 +lon_0=24 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0"
gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

# Database invariant data
kml.file.path <- dbGetQuery(con, "select value from configuration where key = 'KMLFilePath'")
kml.file.path <- kml.file.path$value
log.file.path <- dbGetQuery(con, "select value from configuration where key = 'ProjectRoot'")
log.file.path <- paste(log.file.path$value, "/log", sep="")

# Write out pid to file and record daemon start time
setwd(log.file.path)
pid <- Sys.getpid()
write(pid, file = paste(fname, ".pid", sep = ""))  # Write out pid to new file, overwriting is exists
pstart.string <- paste("KMLgenerate: Daemon starting up at ", format(Sys.time(), "%a %b %e %H:%M:%S %Z %Y"), 
                       " (pid ", pid, ")", sep = "")

# Initialize csv to log database error message
setwd(log.file.path)
log.hdr <- rbind("Error messages from KMLGenerate_X.X.R", 
                 "Time errcode errmessage",
                 "#####################################################################################")
dberrfname <- "KMLGenerate_dbase_error.log"
if(!file.exists(dberrfname)) {
   write.table(log.hdr, file = dberrfname, sep = "", col.names = F, row.names = F, quote = FALSE)
}
options(digit.secs = 4)  # Display milliseconds for time stamps 

# Initialize Rlog file to record daemon start time and which kml ids written and when
rlog.hdr <- rbind("Log of script start, KML ids written and times, from KMLgenerate_X.X.X.R", 
                  "#########################################################################################",
                  "")
logfname <- paste(fname, ".log", sep = "")  # Log file name
if(!file.exists(logfname)) {
  #write(rlog.hdr, file = paste(fname, ".log", sep = ""), col.names = F, row.names = F, quote = FALSE)
  write(rlog.hdr, file = logfname)
}
write(rbind(pstart.string, ""), file = logfname, append = TRUE)  # Write out daemon start stamp

repeat {
  
  # afmap queries
  kml.polling.interval <- dbGetQuery(con, "select value from configuration where key = 'KMLPollingInterval'")
  kml.polling.interval <- as.numeric(kml.polling.interval$value)  
  kml.batch.size <- dbGetQuery(con, "select value from configuration where key = 'NKMLBatchSize'")
  kml.batch.size <- as.numeric(kml.batch.size$value)  # Should be at least 500 to ensure decent weighting
  min.avail.kml <- dbGetQuery(con, "select value from configuration where key = 'MinAvailNKMLTarget'")
  min.avail.kml <- min.avail.kml$value
  #avail.kml.count <- dbGetQuery(con, "select count(*) from kml_data where hit_id is NULL")
  avail.kml.count <- dbGetQuery(con, paste("select count(*) from kml_data left outer join hit_data", 
                                           "using (name) where kml_type = 'N' and create_time is null"))
  avail.kml.count <- avail.kml.count$count
  
  start.time <- Sys.time()  
  #avail.kml.count < 400
  if(avail.kml.count < min.avail.kml) {  # Set pretty high in case HITs are drawn down at rapid rate

	  # Step 1. Poll the database (SouthAfrica) to see which grid IDs are still available
    grid.IDs <- dbGetQuery(con, "select id, fwts from sa1kgrid where avail = 'T'")

    # Step 2. Draw weighted random sample = min.kml.batch
	  set.seed(234)
    id.rand <- sample(grid.IDs$id, size = kml.batch.size, replace = F, prob = grid.IDs$fwts)  # Random draw
    #table(grid.IDs[grid.IDs$id %in% id.rand, "fwts"])
    sql <- paste("SELECT ST_AsEWKT(geom) from sa1kgrid where id in", " (", paste(id.rand, collapse = ","), 
                 ")", sep = "")
	  id.geom <- dbGetQuery(con, sql)  # Get the coordinates for the random grid
    geom.tab <- cbind(id.rand, id.geom)  # IDs and geometries in table
    kmlnames <- rep(NA, nrow(geom.tab))  # set up vector of kml names
    
    # Create and print kmls
    for(i in 1:nrow(geom.tab)) {
      geom.str <- unlist(strsplit(geom.tab[i, 2], ";"))  # Strip out polygon IDs
      geom.poly <- as(readWKT(geom.str[-grep("SRID", geom.str)], p4s = alb), "SpatialPolygonsDataFrame") #SPDF
      colnames(geom.poly@data)[1] <- "ID"  # Rename ID field
    
      # Step 3. Create a file name for the kml
	    geom.poly@data$ID <- geom.tab[i, 1]
      geom.poly@data$kmlname <- paste(country.ID, geom.poly@data$ID, sep = "")  # 19/10/2012
      kmlnames[i] <- geom.poly@data$kmlname  # 19/10/2012
   
      # Step 4. Write out the kml
	    geom.poly.gcs <- spTransform(x = geom.poly, CRSobj = CRS(gcs))  # First convert to geographic coords
      setwd(kml.file.path)  # Change into kml directory
  	  writeOGR(geom.poly.gcs, dsn = paste(geom.poly.gcs@data$kmlname, "kml", sep = "."), 
               layer = geom.poly.gcs@data$kmlname, driver = "KML", dataset_options = c("NameField = name"), 
               overwrite = T)  # Write it
      #print(paste("kml for", geom.poly.gcs@data$kmlname, "written"))
    }
        
    # Update afmap with filename and kml_type
		ret <- dbSendQuery(con, paste("insert into kml_data (name, kml_type) values ", 
                                  paste("('", kmlnames, "', ", "'", kml.type, "')", sep = "", collapse = ","), 
                                  sep = ""))
     # Update SouthAfrica to show grid is no longer available for selecting/writing
    ret2 <- dbSendQuery(con, paste("UPDATE sa1kgrid SET avail='F' where ID in", 
                                    "(", paste(geom.tab[, 1], collapse = ","), ")", sep = ""))
    
    # Database error handling
		exception <- dbGetException(con)  # update exceptions
    # NOTE: I am not quite sure about more formal logging methods, so I have mocked up a text file log 
    # I found some links that might point to something more elegant.
    # http://r.789695.n4.nabble.com/Application-logging-in-R-td896477.html
    # http://stackoverflow.com/questions/1928332/is-there-any-standard-logging-package-for-r
    # Crude solution built into your original code:
	  if(exception$errorNum != 0) {
			print("Error updating SouthAfrica")
      errors <- paste(gsub("EDT", "", Sys.time()), "  ", paste(exception, collapse = "    "))
      write(errors, file = dberrfname, append = T)
			quit(status=exception$errorNum, save="no")
		}
	}
  end.time <- Sys.time()
  
  # Write out kmlID log
  write("**************************************", file = logfname, append = T)
  write(format(start.time, "%a %b %d %X %Y %Z"), file = logfname, append = T)
  write("**************************************", file = logfname, append = T)
  if(avail.kml.count < min.avail.kml) {
    write(id.rand, file = logfname, append = T)
  } else{ 
    write("Sufficient NKMLs are in the system", file = logfname, append = T)
  }
  write("**************************************", file = logfname, append = T)
  write(format(end.time, "%a %b %d %X %Y %Z"), file = logfname, append = T)
  write("**************************************", file = logfname, append = T)
  write("", file = logfname, append = T)
	Sys.sleep(kmlPollingInterval)
}

# After testing, reset changes to the following database fields: 
# SouthAfrica: 
#   avail: Reset avail to 'T' (update sa1kgrid set avail='T' where avail='F')
#   AvailableKMLTarget: set to 500
#   kml_data: Remove test file names





