#kmlid <- "SA9364" 
#kmlid <- "SA27392"  # mismatching id
#kmlid <- "SA33076"  # score seems reasonable
#kmlid <- "SA30336" 
kmlid <- "SA137455"
source("/var/www/html/afmap/R/KMLAccuracyCheck.1.2.R")


if(exists("grid.poly")) bbr1 <- bbox(grid.poly)
if(exists("qaqc.poly")) bbr2 <- bbox(qaqc.poly)
if(exists("user.poly")) bbr3 <- bbox(user.poly)

lbbrls <- ls(pattern = "^bbr")
if(length(lbbrls) > 0) {
  xr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[1, ]))
  yr <- range(sapply(1:length(lbbrls), function(x) get(lbbrls[x])[2, ]))
  vals <- rbind(xr, yr)

#vals <- rbind(range(bbox(grid.poly)[1, ], bbox(qaqc.poly)[1, ]), 
#              range(bbox(grid.poly)[2, ], bbox(qaqc.poly)[2, ]))
#print(vals)

  png(paste(kmlid, ".png", sep = ""), height = 700, width = 700, antialias = "none")
  plot(grid.poly, xlim = vals[1, ], ylim = vals[2, ])
  objchk <- sapply(2:5, function(x) is.object(inres[[x]]))
  mpi <- names(err.out)
  plotpos <- c(0, 0.25, 0.5, 0.75)
  col <- c("green4", "red4", "blue4", "purple")
  for(i in 1:4) {
    if(objchk[i] == "TRUE") plot(inres[[i + 1]], add = T, col = col[i])
    mtext(round(err.out[i], 3), side = 3, line = -1, adj = plotpos[i])
    mtext(mpi[i], side = 3, line = 0, adj = plotpos[i])
    if(exists("user.poly.out")) plot(user.poly.out, add = T, col = "grey")
    if(exists("qaqc.poly.out")) plot(qaqc.poly.out, add = T, col = "pink")
    if(exists("tpo")) plot(tpo, col = "green1", add = T)
    if(exists("fno")) plot(fno, col = "blue1", add = T)
  }
}
dev.off()











