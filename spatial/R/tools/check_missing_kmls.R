# check on no data sites from KMLgenerate runs
rm(list = ls())
suppressMessages(library(rmapaccuracy))
library(data.table)

# Find working location
dinfo <- getDBName()  # pull working environment
kml.path <- paste0(dinfo["project.root"], "/kmls/")

#   source(paste(script.dir, "KMLAccuracyFunctions.R", sep="/"))

# Paths and connections
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")

kmls <- data.table(dbGetQuery(con, "select * from kml_data", 
                              stringAsFactors = FALSE))
selnm <- kmls[!like(name, "ZM|SA"), name]  # non Zambia or SA names

# mapper kmls
nmchk <- sapply(selnm, function(x) {  # x <- hitkml$name[1]  
  file.exists(paste0(kml.path, x, ".kml"))
}) # zm missing
any(nmchk == FALSE)  # all in there

# file.exists(paste0(kml.path, "GA0054464", ".kml"))

