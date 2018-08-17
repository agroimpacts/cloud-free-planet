#' Find correct root path and database name 
#' @param db.sandbox.name Name of development server/database
#' @param db.production.name Name of production server/database
#' @return Root path and database name in named vector 
#' @note The function arguments currently default to Africa*, so expect 
#' these to change with project upgrades
#' @export
get_db_name <- function(db.sandbox.name = 'AfricaSandbox', 
                        db.production.name = 'Africa') {
  info <- Sys.info()
  euser <- unname(info["effective_user"])
  if(euser == "mapper") {
    sandbox <- FALSE
    uname <- "mapper"
  } else {
    sandbox <- TRUE
    uname <- euser
  }
  
  # Project root
  pathv <- strsplit(getwd(), .Platform$file.sep)[[1]]
  sstr <- c("mapper", "mapper_sandbox", "afmap_sandbox", "afmap")
  if(any(sstr %in% pathv)) {
    project.root <- paste0(pathv[1:grep(paste(sstr, collapse = "|"), pathv)], 
                           collapse = .Platform$file.sep)
  } else {
    stop(paste(project.root, "is not a mapper directory"), call. = FALSE)
  }

  # DB Names
  if(sandbox == TRUE) {
    db.name <- db.sandbox.name
  } else {
    db.name <- db.production.name
  }
  
  # # credentials
  # params <- yaml::yaml.load_file(file.path(project.root, 'common/config.yaml'))
  return(c("db.name" = db.name, "project.root" = project.root))
}

#' Find correct root path and database name 
#' @param host NULL is running on crowdmapper, else crowdmapper.org for remote
#' @return Database connection, root path, and database name in list
#' @note The function arguments currently default to SouthAfrica*, so expect 
#' these to change with project upgrades
#' @import DBI
#' @export
mapper_connect <- function(host = NULL) {
  dinfo <- get_db_name()  # pull working environment
  common_path <- file.path(dinfo["project.root"], "common")
  params <- yaml::yaml.load_file(file.path(common_path, 'config.yaml'))
  
  # Paths and connections
  con <- DBI::dbConnect(RPostgreSQL::PostgreSQL(), host = host, 
                        dbname = dinfo["db.name"],   
                        user = params$mapper$db_username, 
                        password = params$mapper$db_password)
  return(list("con" = con, "dinfo" = dinfo, "params" = params))
}


