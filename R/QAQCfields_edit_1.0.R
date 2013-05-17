#! /usr/bin/R -f 
##############################################################################################################
# Title      : QAQCfields_edit_1.0.R
# Purpose    : Fix field names for QAQC fields in database
# Author     : Lyndon Estes
# Draws from : KMLgenerate*.R
# Used by    : 
# Notes      : Created 02/05/2013
#              
##############################################################################################################

library(RPostgreSQL)

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "SouthAfrica", user = "***REMOVED***", password = "***REMOVED***")

country.ID <- "SA"  # Ideally this will be read out of the database, as we expand to other countries

flds <- dbGetQuery(con, "select gid, id, name from qaqcfields")
nas <- which(is.na(flds$name))
newnm <- paste("SA", flds$id[nas], sep = "")
flds[nas, "name"] <- newnm
uninms <- unique(flds$id[nas])

for(i in uninms) {
  sql <- print(paste("UPDATE qaqcfields SET name=", "'", paste("SA", i, sep = ""), "'", 
                     " where id=", i, sep = ""))
  ret2 <- dbSendQuery(con, sql)
  exception <- dbGetException(con)
  print(exception)
}

length(unique(flds$id))

flds2 <- dbGetQuery(con, "select name, fields from newqaqc_sites")

unique(flds$name[!unique(flds$name) %in% flds2$name[flds2$fields == "Y"]])


