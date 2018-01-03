# check on no data sites
rm(list = ls())
suppressMessages(library(rmapaccuracy))
library(data.table)

# Find working location
dinfo <- getDBName()  # pull working environment
kml.path <- paste0(dinfo["project.root"], "/kmls/")
kml.pathst <- paste0(dinfo["project.root"], "/kmls_static/")
kml.pathsb <- "/home/sandbox/afmap/kmls/"
kml.pathsbst <- "/home/sandbox/afmap/kmls_static/"

#   source(paste(script.dir, "KMLAccuracyFunctions.R", sep="/"))

# Paths and connections
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")

# select assignments where image is in the comment
asssql <- paste0("select * from assignment_data where comment like '%image%'")
assignments <- data.table(dbGetQuery(con, asssql))
noimagery <- assignments[like(comment, "no image")]

kmlname <- function(hitid, con) {
  sql <- paste0("SELECT hit_id,name from hit_data WHERE hit_id in (", 
                paste0("'", hitid, "'", collapse = ","), ")")
  hits <- dbGetQuery(con, sql)
  return(hits)
}

hitkml <- data.table(kmlname(noimagery$hit_id, con))  # hits with kmls

# gcs <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

# Collect KMLs from kml folder
uninoimage_kml <- unique(hitkml$name)

# mapper kmls
sapply(uninoimage_kml, function(x) {  # x <- hitkml$name[1]  
  file.exists(paste0(kml.path, x, ".kml"))
}) # zm missing

# mapper kmls_static
sapply(uninoimage_kml, function(x) {  # x <- hitkml$name[1]  
  file.exists(paste0(kml.pathst, x, ".kml"))
})  # zm missing

# sandbox kmls (didn't get copied over)
sapply(uninoimage_kml, function(x) {  # x <- hitkml$name[1]  
  file.exists(paste0(kml.pathsb, x, ".kml"))
})  # all present

# sandbox kmls_static
sapply(uninoimage_kml, function(x) {  # x <- hitkml$name[1]  
  file.exists(paste0(kml.pathsbst, x, ".kml"))
})  # all missing

# check whether these missing ones are in the kml_table
sql <- paste0("select name, kml_type from kml_data where name in (", 
              paste0(paste0("'", unique(hitkml$name), "'", collapse = ","), ")"))
tabchk <- data.table(dbGetQuery(con, sql))  # three N and the rest Q

# Let's check all kmls in table and see if they have corresponding kmls
fnames <- gsub(".kml", "", list.files(kml.path))
sql <- paste0("select name from kml_data")
kmltab <- data.table(dbGetQuery(con, sql))$name  # three N and the rest Q
missingkmls <- kmltab[!kmltab %in% fnames]  # The Zambia sites do not have kmls

# So which ones are causing no image problems
noimagekmls <- tabchk$name[tabchk$name %in% fnames]
kmls <- sapply(noimagekmls, function(x) {  # x <- noimagekmls[1]  
  kml <- readOGR(dsn = paste0(kml.path, x, ".kml"), layer = x)
})  # all missing
sapply(kmls, gCentroid)  # centroids fine for these

kmlstr <- "http://mapper.princeton.edu/api/getkml?kmlName="
sapply(noimagekmls, function(x) paste0(kmlstr, x))

# copy over the missing ones to the right folders
missingkmls_insb <- paste0(kml.pathsb, missingkmls, ".kml")
fixdirs <- c(kml.pathsbst, kml.path, kml.pathst)
for(i in fixdirs) {
  print(i)
  ftocopy <- paste0(i, missingkmls, ".kml")
  if(all(!file.exists(ftocopy))) {
    print(paste("copying to", i))
    file.copy(missingkmls_insb, ftocopy, overwrite = FALSE)
  } else {
    stop("check files properly", call. = FALSE)
  }
}

# recheck if they are all there now
# mapper kmls
sapply(uninoimage_kml, function(x) {  # x <- hitkml$name[1]  
  file.exists(paste0(kml.path, x, ".kml"))
}) # zm missing

# mapper kmls_static
sapply(uninoimage_kml, function(x) {  # x <- hitkml$name[1]  
  file.exists(paste0(kml.pathst, x, ".kml"))
})  # zm missing

# sandbox kmls (didn't get copied over)
sapply(uninoimage_kml, function(x) {  # x <- hitkml$name[1]  
  file.exists(paste0(kml.pathsb, x, ".kml"))
})  # all present

# sandbox kmls_static
sapply(uninoimage_kml, function(x) {  # x <- hitkml$name[1]  
  file.exists(paste0(kml.pathsbst, x, ".kml"))
})  # all missing





