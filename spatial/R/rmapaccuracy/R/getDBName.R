#' Find correct root path and database name 
#' @param db.sandbox.name Name of development server/database
#' @param db.production.name Name of production server/database
#' @return Root path and database name in named vector 
#' @note The function arguments currently default to SouthAfrica*, so expect 
#' these to change with project upgrades
#' @export
getDBName <- function(db.sandbox.name = 'AfricaSandbox', 
                      db.production.name = 'Africa') {
  info <- Sys.info()
  euser <- unname(info["effective_user"])
  if(euser == "sandbox") {
    sandbox <- TRUE
    uname <- "sandbox"
  } else if(euser == "mapper") {
    sandbox <- FALSE
    uname <- "mapper"
  } else {
    stop("Any R script must run under sandbox or mapper user")
  }
  
  project.root <- paste("/home/", uname, "/afmap", sep = "")  # Project root path
  
  if(sandbox == TRUE) {
    db.name <- db.sandbox.name
  } else {
    db.name <- db.production.name
  }
  return(c("db.name" = db.name, "project.root" = project.root))
}
