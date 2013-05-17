#! /usr/bin/R -f 
##############################################################################################################
# Title      : QKML_rerandomize.R
# Purpose    : Script for developing random ordering of QAQC ids, splicing in field and non-field QAQCs in 
#              regular intervals
# Author     : Lyndon Estes
# Draws from : KMLgenerate*.R
# Used by    : 
# Notes      : Created 20/4/2013
#              Current QAQCs are at ration of 205 with fields and 609 without
#              13/5/2013: Updated QAQCs in kml_data at a rate of 1:1 fields to non-fields QAQCs
##############################################################################################################

library(RPostgreSQL)

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "SouthAfrica", user = "***REMOVED***", password = "***REMOVED***")

# Hardcoded data
country.ID <- "SA"  # Ideally this will be read out of the database, as we expand to other countries
kml.type <- "Q"  # Type of KML (N for non-QAQC)

# Step 1. Version 1 (Use all QAQCs) Download existing sample dataset and reorder fields and non-fields QAQC
# grid.IDs <- dbGetQuery(con, "select name, fields from newqaqc_sites")
# ratio <- nrow(grid.IDs[grid.IDs$fields == "N",  ]) / nrow(grid.IDs[grid.IDs$fields == "Y",  ]) # Ratio N:Y
# 
# newIDs <- data.frame(matrix(nrow = nrow(grid.IDs), ncol = 2))  # Dummy for reordering
# colnames(newIDs) <- colnames(grid.IDs)
# newIDs2 <- newIDs  # Second dummy 
# # Select out fields and non-fields locations and reorder them
# flds.rand <- grid.IDs[grid.IDs$fields == "Y",  ][sample(1:nrow(grid.IDs[grid.IDs$fields == "Y",  ])), ]
# nflds.rand <- grid.IDs[grid.IDs$fields == "N",  ][sample(1:nrow(grid.IDs[grid.IDs$fields == "N",  ])), ]
# newIDs[round(seq(1, nrow(grid.IDs), ratio + 1)), ] <- flds.rand  # Splice in fields every 3rd row
# newIDs[is.na(newIDs$name), ] <- nflds.rand  # Fill in 2 non-fields between every field

# Slightly perturb the result so that the order isn't exactly 2 non-fields between every field
# set.seed(231)
# v <- seq(sample(1:10, 1), nrow(newIDs), 10)  # Random starting row from first 10 rows, then every 10 thereaft 
# ii <- sample(c(rep(-2, 1), rep(-1, 5), rep(1, 5), rep(2, 1)), length(v), replace = TRUE)  # Random perturb
# # Pull out row and the one selected near (distance based on ii), then swap their indices and values in newIDs2
# for(i in 1:length(v)) {
#   inds <- c(v[i], v[i] + ii[i])
#   vs <- newIDs[inds, ]
#   newIDs2[inds, ] <- vs[2:1, ]
# }
# newIDs2[is.na(newIDs2$name), ] <- newIDs[is.na(newIDs2$name), ]  # Fill in the rest of newIDs with undisturbed
# #all(newIDs[order(newIDs$name), "fields"] == newIDs2[order(newIDs2$name), "fields"])  # Check 
# #all(newIDs[order(newIDs$name), "name"] == newIDs2[order(newIDs2$name), "name"])  # Check

# # Step 2. Update database
# # First change "Q" values in existing database to "X", for later clean-up
# ret <- dbSendQuery(con, paste("UPDATE kml_data SET kml_type='X' where name in", 
#                                 "(", paste("'", newIDs2$name, "'", collapse = ",", sep = ""), ")", sep = ""))
# 
# ret <- dbSendQuery(con, paste("insert into kml_data (kml_type, name) values ", 
#                               paste("('", "Q", "', ", "'", newIDs2$name, "')", sep = "", collapse = ","), 
#                               sep = ""))


# Step 1. Version 2: Use 1 non-fields QAQC for every QAQC with fields
grid.IDs <- dbGetQuery(con, "select name, fields from newqaqc_sites")
nflds <- nrow(grid.IDs[grid.IDs$fields == "Y",  ]) # N QAQCs with fields
newIDs <- data.frame(matrix(nrow = nflds * 2, ncol = 2))  # Dummy for reordering
colnames(newIDs) <- colnames(grid.IDs)

# Select out fields and non-fields locations and reorder them - this version select n no fields = n fields
flds.rand <- grid.IDs[grid.IDs$fields == "Y",  ][sample(1:nrow(grid.IDs[grid.IDs$fields == "Y",  ])), ]
set.seed(231)
nflds.rand <- grid.IDs[grid.IDs$fields == "N",  ][sample(1:nrow(grid.IDs[grid.IDs$fields == "N",  ]), 
                                                         size = nflds), ]
newIDs[round(seq(1, nrow(newIDs), 2)), ] <- flds.rand  # Splice in fields every 3rd row
newIDs[is.na(newIDs$name), ] <- nflds.rand  # Fill in 2 non-fields between every field


# Step 2. Update database
# First change "Q" values in existing database to "X", for later clean-up
# ret <- dbSendQuery(con, paste("UPDATE kml_data SET kml_type='Q' where name in", 
#                                 "(", paste("'", newIDs$name, "'", collapse = ",", sep = ""), ")", sep = ""))

ret <- dbSendQuery(con, paste("insert into kml_data (kml_type, name) values ", 
                              paste("('", "Q", "', ", "'", newIDs$name, "')", sep = "", collapse = ","), 
                              sep = ""))





