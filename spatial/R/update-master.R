# update-master.R
# Create/update master grid in database
# Note: script needs to be run from terminal as user sandbox/mapper, not 
# Rstudioserver, as psql with password only works from command line

suppressMessages(library(RPostgreSQL))
suppressMessages(library(rmapaccuracy))
# library(devtools)
# install_github('wrswoR', 'krlmlr')
suppressMessages(require(wrswoR))
suppressMessages(require(data.table))

# Determine working directory and database
dinfo <- getDBName()  # pull working environment
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")

# Create table first if it doesn't exist for some reason
if(!dbExistsTable(con, "master_grid")) {
  sql <- paste("CREATE TABLE master_grid",
               "(gid serial PRIMARY KEY,",
               "id integer, x double precision,",
               "y double precision, name varchar, pr double precision,", 
               "fwts integer, zone integer, avail char(1))")
  dbSendQuery(con, sql)
  dbSendQuery(con, paste0("CREATE INDEX name_gix ON master_grid (id, name, ", 
                          "fwts, zone, avail)"))
  dbSendQuery(con, "VACUUM ANALYZE master_grid")
  dbSendQuery(con, "CLUSTER master_grid USING name_gix")
}

# Read in master table counter data

## Tests
# sql <- c("UPDATE master_grid_counter SET counter = 0")
# dbSendQuery(con, sql)
# sql <- paste("UPDATE master_grid_counter SET counter = 1496218",  
#              "WHERE block in (1, 2)")
# dbSendQuery(con, sql)
# sql <- paste("UPDATE master_grid_counter SET counter = 50000", 
#              "WHERE block in (3)")
# dbSendQuery(con, sql)
###

sql <- paste("SELECT * from master_grid_counter ORDER BY block")
count_tab <- data.table(dbGetQuery(con, sql), key = "block")
if(count_tab[, sum(counter)] == 0) {
  active_block <- count_tab[1, ]
} else {
  active_block <- count_tab[counter < max(nrows), .SD[1]]
}

# Select master grid sub-block csv. The active block if the counter is at 0, or 
# the next block if there are only 1000 records left before it hits the number 
# of rows in the block. Otherwise, shouldn't be selecting a new group.  
if(active_block$counter == 0) {
  subgrid <- paste0(dinfo["project.root"], 
                    "/spatial/data/gridfiles/africa_master_grid_sub", 
                    active_block$block, ".csv")
} else if(between(active_block$counter, active_block$nrows - 1000, 
                  active_block$nrows)) {
  subgrid <- paste0(dinfo["project.root"], 
                    "/spatial/data/gridfiles/africa_master_grid_sub", 
                    active_block$block + 1, ".csv")
} else {
  stop("Updating grid shouldn't happen yet", call. = FALSE)
}

# Clean out completed rows in master (avail = F)
dbSendQuery(con, "DELETE from master_grid where avail='F'")

# Update by appending
# Write sql command to file gridupdate.sql
psql <- paste("\\copy master_grid(id, x, y, name, pr, fwts, zone, avail) FROM", 
              subgrid, "WITH DELIMITER ',' CSV HEADER")
write(psql, file = paste0(dinfo["project.root"], "/pgsql/gridupdate.sql"))

# Run system call to psql, which will update table with rows
pgsql <- paste0("set PGPASSWORD=Afr1c@; psql -d ", dinfo["db.name"], 
                " -U postgres -f ", dinfo["project.root"], 
                "/pgsql/gridupdate.sql")
system(pgsql, intern = TRUE)

dbSendQuery(con, "VACUUM ANALYZE master_grid")
dbSendQuery(con, "CLUSTER master_grid USING name_gix")
