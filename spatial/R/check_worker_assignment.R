#! /usr/bin/Rscript
# Purpose    : Script for retrieving worker assignments

# Libraries
# suppressMessages(library(RPostgreSQL))
suppressMessages(library(rmapaccuracy))
suppressWarnings(suppressMessages(library(sf)))

# Get HIT ID, assignment ID
args <- commandArgs(TRUE)
if(length(args) < 3) stop("Need at least 3 arguments")
# hitid <- '30'; workerid <- "24"; test_root <- "Y"; testlocal <- "TRUE"
hitid <- args[1] 
workerid <- args[2]   
test_root <- args[3] 

# Find working location
# dinfo <- c(db.name = "AfricaSandbox",
#            project.root = "/Users/lestes/Dropbox/projects/activelearning/mapperAL")
dinfo <- getDBName()  # pull working environment

initial_options <- commandArgs(trailingOnly = FALSE)
kml_path <- paste0(dinfo["project.root"], "/maps/")
kml_root <- strsplit(dinfo["project.root"], "/")[[1]][3]

if(test_root == "Y") {
  print(paste("database =", dinfo["db.name"], "; kml.root =", kml_root, 
              "; worker kml directory =", kml_path, "; hit =", hitid))
  print(paste("Stopping here: Just making sure we are working and writing to", 
              "the right places"))
} 

if(test_root == "N") {
  
  # Paths and connections
  # host <- ifelse(!getwd() %in% c("/home/sandbox/afmap/", "/home/africa/afmap/"), 
  #                "crowdmapper.org", "")
  con <- DBI::dbConnect(RPostgreSQL::PostgreSQL(), #host = host, 
                        dbname = dinfo["db.name"],   
                        user = pgupw$user, password = pgupw$password)
  
  # Read in hit and assignment ids  
  hits <- tbl(con, "hit_data") %>% filter(hit_id == hitid) %>%
    select(name) %>% collect()
  assignments <- tbl(con, "assignment_data") %>% 
    filter(hit_id == hitid & worker_id == workerid) %>% 
    select(assignment_id) %>% collect()
  
  if(nrow(assignments) > 1) {
    stop("More than one assignment for this worker for this HIT")
  }
  
  # Collect QAQC fields (if there are any; if not then "N" value will be 
  # returned). This should work for both
  # training and test sites
  qaqc_sql <- paste0("select gid, geom_clean",
                     " from qaqcfields where name=", "'", hits$name, "'")
  qaqc_polys <- suppressWarnings(st_read_db(con, query = qaqc_sql, 
                                            geom_column = 'geom_clean'))
  
  # Read in user data
  user_sql <- paste0("select name, geom_clean from user_maps where ",
                     "assignment_id=", "'", assignments$assignment_id, "'",
                     " order by name")
  user_polys <- suppressWarnings(st_read_db(con, query = user_sql, 
                                            geom_column = 'geom_clean'))
  
  # Create unique directory for worker if file doesn't exist
  worker_path <- paste(kml_path, workerid, sep = "")
  if(!file.exists(worker_path)) dir.create(path = worker_path)
  
  # Write KMLs out to worker specific directory
  # setwd(worker_path)
  # nm <- paste(hits$name, assignments$assignment_id, sep = "_")
  kmlid <- hits$name
  if(nrow(user_polys) > 0) {  # Write it
    suppressWarnings(user_poly <- user_polys %>% 
                       transmute(kmlname = paste0(kmlid, "_w")))
    suppressWarnings(write_sf(user_poly, delete_dsn = TRUE,
                              dsn = paste0(worker_path, "/", kmlid, "_w.kml")))
  }
  if(nrow(qaqc_polys) > 0) {  # First convert to geographic coords
    suppressWarnings(qaqc_poly <- qaqc_polys %>% 
                       transmute(kmlname = paste0(kmlid, "_r")))
    suppressWarnings(write_sf(qaqc_poly, delete_dsn = TRUE,
                              dsn = paste0(worker_path, "/", kmlid, "_r.kml")))
  }
  worker_url <- paste0("https://", kml_root, 
                       ".crowdmapper.org/api/getkml?kmlName=", kmlid, 
                       "&workerId=", workerid)
  cat(worker_url, "\n") # Return details
}
