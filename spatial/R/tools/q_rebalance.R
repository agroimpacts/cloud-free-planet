#! /usr/bin/Rscript
# q_rebalance.R
# Change distribution of Q sites to match those of N and F_select
# NOTE (7/6/2016): checked that fwts were correct after running "read" option by
#  comparing kml_data_static and kml_data. Checked that reordering is
#  reproducible with random seed, after running clear_db.sh. 

## Clear console and load required packages
rm(list=ls(all=TRUE))
library(data.table)
library(rmapaccuracy)

# Rebalance or pare down Q sites from list of names in input data object?
# "read" or "rebalance"
qoption <- "read"  # default option

## Set working directory
dinfo <- getDBName()  # pull working environment
setwd(paste0(dinfo["project.root"], "/spatial/data"))

## Connect to database
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")

# set up little function for pasting values in SQL insert format
insert_paster <- function(intab) {
  paste0("(", paste0(sapply(1:ncol(intab), function(x) {
    val <- intab[[x]]
    if(class(val) == "character" | class(val) == "logical") {
      valo <- paste0("'", val, "'")
    } else {
      valo <- paste0(val)
    }
  }), collapse = ","), ")") 
}

# Retrieve Q sites
sql1 <- paste0("SELECT * from kml_data where kml_type='Q'") 
qfwts_tab <- data.table(dbGetQuery(con, sql1))
qfwts_tab <- qfwts_tab[order(gid), ]

# Read option: reset kml_data to match list of input names in spatial/qsites
# This option is to be used after clear_db.sh
if(qoption == "read") {
  load("qsites/qsites.rda")
  
  # pare down list to just those in qsites
  qnon_tab <- copy(qfwts_tab[(name %in% qsites)])
  
  # delete all Q records, because we want to reset GIDs
  sql <- paste0("DELETE from kml_data WHERE kml_type='Q'")
  dbSendQuery(con, sql)
  dbSendQuery(con, "VACUUM ANALYZE kml_data")
  
  # reset gids update gids for I sites
  sql <- paste0("SELECT * from kml_data WHERE kml_type='I'")
  i_tab <- data.table(dbGetQuery(con, sql))
  i_tab <- i_tab[order(gid)]
  for(i in 1:length(i_tab$gid)) {
    sql <- paste0("UPDATE kml_data SET gid=", i, " WHERE name='", 
                  i_tab[i, name], "'")
    dbSendQuery(con, sql)
    lastgid <- i
  }
  
  # add back in Q KMLs after shuffling and adjusting GIDs
  set.seed(234)
  qord <- sample(1:nrow(qnon_tab), size = nrow(qnon_tab), replace = FALSE)
  qnon_tab_reord <- qnon_tab[qord, ]
  qnon_tab_reord[, gid := (lastgid + 1):(lastgid + .N)]
  
  for(i in 1:nrow(qnon_tab_reord)) {  # i <- 1
    intab <- copy(qnon_tab_reord[i, ])
    sqlrt <- insert_paster(intab)
    insertrt <- paste0("(gid,kml_type,name,hint,mapped_count,", 
                       "post_processed,fwts)")
    sql <- paste0("INSERT into kml_data", insertrt, " values ", sqlrt)
    dbSendQuery(con, sql)
  }
  dbSendQuery(con, "VACUUM ANALYZE kml_data")
  
  # set availability to false for any Q names in the master_grid
  sql <- paste0("SELECT name from kml_data") 
  qnms_new <- dbGetQuery(con, sql)$name  # names in kml_data
  sql <- paste0("UPDATE master_grid SET avail='F' WHERE name in (", 
                paste0("'", qnms_new, "'", collapse = ","), ")")
  dbSendQuery(con, sql)
  dbDisconnect(con)
}
  
# The below is Drew's code for rebalancing based on fwt distribution matching. 
# Not really tested, but possibly can be used for future adjustment of Q sites 
# while project in motion, rather than immediately after clear_db.sh. 
# An example is to use it after the f_ and n_select sites have been added. 
if(qoption == "rebalance") {
  # Retrieve Q site weights
  sql1 <- paste0("SELECT name, fwts from kml_data where kml_type='Q'") 
  qfwts_tab <- data.table(dbGetQuery(con, sql1))
  colnames(qfwts_tab) <- c("name", "fwts")
  
  # Retrive names of q sites with and without fields
  sql2 <- paste0("SELECT name from qaqcfields")
  qaqc_tab <- data.table(dbGetQuery(con, sql2))
  qaqc_tab <- unique(qaqc_tab)
  qffwts_tab <- qfwts_tab[name %in% qaqc_tab$name]
  qnfwts_tab <- qfwts_tab[!(name %in% qaqc_tab$name)]
  qsel_tab <- rbind(qffwts_tab, qnfwts_tab[fwts > 1])
  qord <- sample(qnfwts_tab[fwts == 1]$name, 
                 size = ceiling(0.05 * nrow(qnfwts_tab[fwts == 1])))
  qran_tab <- qnfwts_tab[name %in% qord]
  qtot_tab <- rbind(qsel_tab, qran_tab)
  qnon_tab <- qfwts_tab[!(name %in% qtot_tab$name)]
  
  # Check histogram
  qtfwts <- qtot_tab$fwts
  pqtfwts <- hist(qtfwts, breaks = seq(0, 10), plot = FALSE)$density
  barplot(pqtfwts, 
          names.arg = c("1", "2", "3", "4", "5", "6", "7", "8", "9", "10"), 
          ylim = c(0, 1), ylab = "Density", xlab = "Fwts", 
          main = "Distribution of new Q sites")
  
  
  ## Update kml_data by deleting q sites not used
  sqlrt <-  paste0(qnon_tab$name, collapse = "', '")
  sql <- paste0("DELETE from kml_data WHERE name IN ('", sqlrt, "')")
  dbSendQuery(con, sql)
  dbSendQuery(con, "VACUUM ANALYZE kml_data")
}