# Continued testing and development for KMLAccuracyCheck.*.R

#kmlids <- paste("SA", 
#                c(137455, 56953, 69741, 71817, 78246, 108041, 144765, 125066, 225717, 133386, 116200), 
#                sep = "")
# kmlids <- paste("SA", 
#                 c(46951,  # This is location with no qaqc site and no user maps case 1
#                   103326, # Case 1
#                   116000, # Case 1
#                   132832, # QAQC + user with overlaps case 2 
#                   175522, # Case 4 with overlaps
#                   364154, # Case 2 (but incorrect--should be Case 4)
#                   549276,  # Case 3: 
#                   597751  # Case 3: 
#                 ), 
#                 sep = "")
# for(i in 1:length(kmlids)) {
#   kmlid <- kmlids[i]   
#   print(kmlid)
#   source("/var/www/html/afmap/R/KMLAccuracyCheck.1.2.1.R")
# }

# Testing errors on 5/4/2013
assignmentid <- "2ZV6XBAT2D5NWNLKRSH0MG5TYBQ154"
source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")  # 0.7504286 0.7142857 0 0.97 7

assignmentid <- "2M8W40SPW1INS6ED2TA3QAB6B4P1E5"
source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")  # 0.693 0 0 0.99 2

assignmentid <- "2U4CVLL3CA33S6842T39QQU7XMMZ9I"
source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")  # 0.7504286 0.7142857 0 0.97 7
#source("/Volumes/web/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")

assignmentid <- '29PR24SMEZZ2S7I1ZYL8S9Y38PIJ2M'  # This one throws a problem
source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")
plot(qaqc.poly)
plot(user.poly)

# Now to test a bunch in sequence to see if the fixes on 5/4/2013 are robust
suppressMessages(library(RPostgreSQL))
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "SouthAfrica", user = "***REMOVED***", password = "***REMOVED***")
ass.sql <- "select assignment_id, hit_id, worker_id, score from assignment_data"
tab <- dbGetQuery(con, ass.sql)
tab <- tab[!is.na(tab$score), ]
rm(con)
#i <- 50
#for(i in 1:nrow(tab)) {
for(i in c(1:49, 51:60)) {
  assignmentid <- tab$assignment_id[i]
  print(paste("Checking assignment ID", assignmentid))
  source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")  # 0.693 0 0 0.99 2      
}

rm(list = ls())

assignmentid <- '3GD6L00D3SXOZF0MD0WG4CLQ0DR1MW'
# setwd("..")
# source("/var/www/html/afmap/R/KMLAccuracyCheck.R")

