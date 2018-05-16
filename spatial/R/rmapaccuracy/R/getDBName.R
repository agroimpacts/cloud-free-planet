#' Find correct root path and database name 
#' @param db.sandbox.name Name of development server/database
#' @param db.production.name Name of production server/database
#' @param db.tester.name Name of non-sandbox user, for testing
#' @param alt.root An alternative root, for testing off of mapper VM
#' @return Root path and database name in named vector 
#' @note The function arguments currently default to Africa*, so expect 
#' these to change with project upgrades
#' @export
getDBName <- function(db.sandbox.name = 'AfricaSandbox', 
                      db.production.name = 'Africa', 
                      db.tester.name = NULL, alt.root = NULL) {
  info <- Sys.info()
  euser <- unname(info["effective_user"])
  if(euser == "sandbox") {
    sandbox <- TRUE
    uname <- "sandbox"
  } else if(euser == "mapper") {
    sandbox <- FALSE
    uname <- "mapper"
  } else if(!is.null(db.tester.name)) {
    if(euser == db.tester.name) {
      sandbox <- TRUE
      uname <- "sandbox"
    }
  }
  else {
    stop("Any R script must run under sandbox or mapper user")
  }

  # Project root path  
  if(!is.null(alt.root)) {
    project.root <- alt.root
  } else {
    project.root <- paste("/home/", uname, "/afmap", sep = "")  
  }
  
  # DB Names
  if(sandbox == TRUE) {
    db.name <- db.sandbox.name
  } else {
    db.name <- db.production.name
  }
  return(c("db.name" = db.name, "project.root" = project.root))
}

## testing code ## connect testing tables 
# getDBName <- function(db.sandbox.name = 'africa_master_grid_gcs_500',
#                       db.production.name = 'Africa') {
#   info <- Sys.info()
#   euser <- unname(info["effective_user"])
#   if(euser == "sye") {
#     #change euser into to programmer name for testing SY
#     sandbox <- TRUE
#     uname <- "sandbox"
#   } else if(euser == "mapper") {
#     sandbox <- FALSE
#     uname <- "mapper"
#   } else {
#     stop("Any R script must run under sandbox or mapper user")
#   }
# 
#   project.root <- paste("/home/", uname, "/afmap", sep = "")  # Project root path
# 
#   if(sandbox == TRUE) {
#     db.name <- db.sandbox.name
#   } else {
#     db.name <- db.production.name
#   }
#   return(c("db.name" = db.name, "project.root" = project.root))
# }

#' Find correct root path and database name 
#' @param user User name for mapper database
#' @param password Password for mapper database
#' @param host NULL is running on crowdmapper, else crowdmapper.org for remote
#' @param db.tester.name Name of non-sandbox user, for testing
#' @param alt.root An alternative root, for testing off of mapper VM
#' @return Database connection, root path, and database name in list
#' @note The function arguments currently default to SouthAfrica*, so expect 
#' these to change with project upgrades
#' @export
mapper_connect <- function(user, password, host = NULL, 
                           db.tester.name = NULL, alt.root = NULL) {
  # pull working environment
  dinfo <- getDBName(db.tester.name = db.tester.name, alt.root = alt.root)
  # Paths and connections
  con <- DBI::dbConnect(RPostgreSQL::PostgreSQL(), host = host, 
                        dbname = dinfo["db.name"],   
                        user = user, password = password)
  return(list("con" = con, "dinfo" = dinfo))
}


