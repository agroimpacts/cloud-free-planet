# Examine KMLaccuracy failures

rm(list = ls())
library(rmapaccuracy)
library(yaml)
params <- yaml.load_file('../../../common/config.yaml')
prjsrid <- 102022
count.err.wt <- 0.1  
in.err.wt <- 0.7  
out.err.wt <- 0.2  
err.switch <- 1  ### 5/2/2016 Changed to 1
comments <- "T"
write.err.db <- "F"  
draw.maps  <- "F"  
test <- "N"  
test.root <- "N"  
user <- params$mapper$db_username
password <- params$mapper$db_password
mtype <- "qa"
tryid <- NULL

name_hit <- function(assid, con) {
  sql <- paste0("SELECT * from assignment_data WHERE assignment_id in (", 
                paste0("'", assid, "'", collapse = ","), ")")
  asses <- dbGetQuery(con, sql)
  sql <- paste0("SELECT hit_id,name from hit_data WHERE hit_id in (", 
                paste0("'", asses$hit_id, "'", collapse = ","), ")")
  hits <- dbGetQuery(con, sql)
  return(hits)
}

## Set working directory
dinfo <- getDBName()  # pull working environment
b_path <- paste0(dinfo["project.root"], "/mturk/tools/")
setwd(b_path)


## Connect to database
dinfo <- getDBName()  # pull working environment
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = params$mapper$db_username, 
                 password = params$mapper$db_password)

# assignment ID
# assignmentid <- "3N2BF7Y2VQUZ3QL0FP22D2G0M4FHMP"
# assignmentid <- "3TOK3KHVJTIQA400FWV3ETGB3YT7OH"
# assignmentid <- "3RKNTXVS3MY4PDOG3FSEAMCWN19A4J"
nm <- name_hit(assignmentid, con)
kmlid <- nm$name

# first test
KMLAccuracy(mtype = mtype, kmlid = kmlid, assignmentid = assignmentid, 
            tryid = tryid, prjsrid = prjsrid, count.err.wt = count.err.wt, 
            in.err.wt = in.err.wt, out.err.wt = out.err.wt, 
            err.switch = err.switch, comments = comments, 
            write.err.db = write.err.db, draw.maps = draw.maps, test = test,  
            test.root = test.root, user = user, password = password)





