#' Find correct root path and database name 
#' @return Root path and database name in named vector 
#' @note The function arguments currently default to Africa*, so expect 
#' these to change with project upgrades
#' @export
get_db_name <- function() {
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
  project_root <- file.path(Sys.getenv("HOME"), "mapper")
  
  # Parse config
  common_path <- file.path(project_root, "common")
  params <- yaml::yaml.load_file(file.path(common_path, 'config.yaml'))

  # DB Names
  if(sandbox == TRUE) {
    db_name <- params$mapper$db_sandbox_name
  } else {
    db_name <- params$mapper$db_production_name
  }
  
  # # credentials
  # params <- yaml::yaml.load_file(file.path(project.root, 'common/config.yaml'))
  olist <- list("db_name" = db_name, "project_root" = project_root, 
                "user" = params$mapper$db_username, 
                "password" = params$mapper$db_password)
  return(olist)
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
  # common_path <- file.path(dinfo["project.root"], "common")
  # params <- yaml::yaml.load_file(file.path(common_path, 'config.yaml'))
  
  # Paths and connections
  con <- DBI::dbConnect(RPostgreSQL::PostgreSQL(), host = host, 
                        dbname = dinfo$db_name,   
                        user = dinfo$user, 
                        password = dinfo$password)
  return(list("con" = con, "dinfo" = dinfo))
}


