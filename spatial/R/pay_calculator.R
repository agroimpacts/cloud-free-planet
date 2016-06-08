### Calculations to determine optimal payment rates
rm(list=ls(all=TRUE))
library(data.table)
library(RPostgreSQL)
library(rmapaccuracy)
library(raster)
library(data.table)
library(dtraster)

# Set working directory and load data
setwd("/var/local/as/afmap_sandbox/changes/Rmd")
load("trial_data.Rda")

# Connect to database
dinfo <- getDBName()  # pull working environment
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = dinfo["db.name"], user = "***REMOVED***", 
                 password = "***REMOVED***")

# Define constants
frep <- 20
qprop <- 0.2
workers <- 100
qual_fee <- 1.2 # $
flat_fee <- 0.05 # $
diff_inc <- 0.05 # $
bon_inc <- 0.25 # $
cf <- c(0.17, -0.016)  # polynomial coefficients

# Retrieve preliminary N and F site weights
sql <- paste0("SELECT kml_type, fwts from kml_data")
fwts_tab <- data.table(dbGetQuery(con, sql))
colnames(fwts_tab) <- c("type", "wgt")
nfwts <- fwts_tab[fwts_tab$type == "N"]
ffwts <- fwts_tab[fwts_tab$type == "F"]
# ffwts <- rbindlist(list(ffwts, ffwts, ffwts, ffwts))
qfwts <- fwts_tab[fwts_tab$type == "Q"]
ifwts <- fwts_tab[fwts_tab$type == "I"]

# Combine in the proper frequencies
nqsites <- (qprop / (1 - qprop)) * (nrow(nfwts) + frep * nrow(ffwts))
tfwts <- c(nfwts$wgt, rep(ffwts$wgt, frep), 
           rep(qfwts$wgt, ceiling(nqsites / nrow(qfwts))))
pfwts <- hist(tfwts, breaks = seq(0, 10), plot = FALSE)$density

# Get weights for all of africa
br <- brick("~/afmap/spatial/data/shapes/africa_master_brick.tif")
br_dt <- as.data.table.raster(br, xy = TRUE, progress = "text")
setnames(br_dt, old = colnames(br_dt)[3:7], 
         new = c("ID", "pr", "fwts", "cnt_code", "zone"))
br_dt <- br_dt[!is.na(ID)]
pfwts_af <- hist(br_dt$fwts, breaks = seq(0, 10), plot = FALSE)$density


# Retrive time data from trials
setkey(mtdat_dt, wgt_geow)
times <- mtdat_dt[, mean(atime2, na.rm = TRUE), by = wgt_geow] # min
skill <- mtdat_dt[, max(smu2, na.rm = TRUE), by = worker_id]

# Fit data to cubic equation
rhs <- times$V1[1:9]
wgts <- times$wgt_geow[1:9]
mat <- matrix(c(wgts^3, wgts^2, wgts, rep(1, 9)), ncol = 4)
coef <- qr.solve(t(mat) %*% mat) %*% t(mat) %*% rhs
# times_fit <- coef[1]*times$wgt_geow^3 + coef[2]*times$wgt_geow^2 + 
#   coef[3]*times$wgt_geow + coef[4]
fwts <- seq(1, 10)
# times_fit <- round(20 / (1 + exp(-0.9 * ((fwts - 1) - 3.5))), 2)
times_fit <- 10 / 60 + 5.5 * (fwts - 1) +  -0.5 * (fwts - 1)^2  # polynomial 
# plot(times_fit)

# Define function to determine difficulty fee
diff_fees <- function(fwts, method) {
  if (method == "linear") {
    fees <- diff_inc * (fwts - 1)
  } else if (method == "power") {
    fees <- round(diff_inc * ((fwts - 1) ^ 2) / 3, 2)
  } else if (method == "logistic") {
    fees <- round(diff_inc * 27 / (1 + exp(-1.5 * ((fwts - 1) - 4.5))), 2)
  } else if (method == "polynomial") {
    fees <- round(cf[1] * (fwts - 1) + cf[2] * (fwts - 1)^2, 2)
  } else {
    fees <- "Error: Unknown method"
  }
  return(fees)
}

# Calculate hourly rates by difficulty and skill
method <- "polynomial"
bonus <- qprop * bon_inc * seq(0, 4) # $
fwts <- seq(1, 10) # dim
rates <- matrix(NA, length(bonus), length(fwts))
for(i in 1: length(bonus)) {  # i <- 1
  rates[i, ] <- (bonus[i] + flat_fee + diff_fees(fwts, method)) / 
    (times_fit / 60)
}

# Calculate average hourly rate by bonus
avg_rates <- rates %*% pfwts


## Calculate costs for current project
# Model worker skill level using geometric distribution
#skill_fit <- dgeom(seq(0, 4), 0.5) / sum(dgeom(seq(0, 4), 0.5))
skill_fit <- c(0, 0, 0, 0, 1)

# Calculate costs
# hist(ffwts$wgt)
# hist(diff_fees(nfwts$wgt, method))
ncost <- flat_fee * nrow(nfwts) + sum(diff_fees(nfwts$wgt, method))
fcost <- flat_fee * frep * nrow(ffwts) + 
  sum(diff_fees(rep(ffwts$wgt, frep), method))
# qcost <- flat_fee * ceiling(nqsites / nrow(qfwts)) * nrow(qfwts) + 
#   sum(diff_fees(rep(qfwts$wgt, ceiling(nqsites / nrow(qfwts))), method)) + 
#   sum(sample(x = bonus, size = ceiling(nqsites / nrow(qfwts)) * nrow(qfwts), 
#          prob = skill_fit, replace = TRUE))

# N Q sites
nq <- (nrow(nfwts) + frep * nrow(ffwts)) * 0.25  # n qsites
nqw <- round(nq * (table(qfwts$wgt) / nrow(qfwts)))  # by fwts
nqwv <- unlist(sapply(1:9, function(x) rep(as.numeric(names(nqw)[x]), nqw[x])))
qcost <- flat_fee * nq + sum(diff_fees(nqwv, method)) + 
  sum(sample(x = bonus, size = nq, prob = skill_fit, replace = TRUE))

icost <- qual_fee * workers
tcost <- ncost + fcost + qcost + icost

diff_fees(1:10, method)



