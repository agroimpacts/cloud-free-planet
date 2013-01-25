#kmlid <- "SA9364" 
#kmlid <- "SA27392"  # mismatching id
#kmlid <- "SA33076"  # score seems reasonable
#kmlid <- "SA30336" 
#kmlids <- paste("SA", 
#                c(137455, 56953, 69741, 71817, 78246, 108041, 144765, 125066, 225717, 133386, 116200), 
#                sep = "")
kmlids <- paste("SA", 
                c(46951,  # This is location with no qaqc site and no user maps case 1
                  103326, # Case 1
                  116000, # Case 1
                  132832, # QAQC + user with overlaps case 2 
                  175522, # Case 4 with overlaps
                  364154, # Case 2 (but incorrect--should be Case 4)
                  549276,  # Case 3: 
                  597751  # Case 3: 
                ), 
                sep = "")
for(i in 1:length(kmlids)) {
  kmlid <- kmlids[i]   
  print(kmlid)
  source("/var/www/html/afmap/R/KMLAccuracyCheck.1.2.1.R")
}

# Test 28/11
rm(kmlid)
assignmentid <- "286PLSP75KLMCLHI0Z8QHQVJRSKZTB"
source("/Volumes/web/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.1.test.R")
#source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.1.test.R")
rm(list = ls())

# Test 29/11
rm(kmlid)
assignmentid <- "2118D8J3VE7WYHR2A173PCK8AI3YI7"
source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")
rm(list = ls())

# Fixed
# Retest
assignmentid <- "22FQQ7Q67051W9A23QTTTC1XM4SWCB"
assignmentid <- "2TNCNHMVHVKCPPZGWRY4M79KQKI42Q"
assignmentid <- "286PLSP75KLMCLHI0Z8QHQVJRSKZTB"
assignmentid <- "29UMIKMN9U8PFN1N5LNXL3SUY7NSBE"
assignmentid <- "2ZBWKUDD8XMB9F1OBP26XTO6TTFNC4"
assignmentid <- "2OAUUU00OQKKGTGX4XJ2X26803XVVS"
source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")

# Checking null error reported by Dennis at 21.30 on 29/11
assignmentid <- "2ZV6XBAT2D5NWNLKRSH0MG5TYBQ154"
source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")

assignmentid <- "2M8W40SPW1INS6ED2TA3QAB6B4P1E5"
source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")

# Log fail at 17:36 on 30/11/2012
assignmentid <- "2U4CVLL3CA33S6842T39QQU7XMMZ9I"
source("/var/www/html/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")
#source("/Volumes/web/afmap/R/Test_and_Old_R/KMLAccuracyCheck.1.2.2.t.R")

# Invalid geometry found on SA671384, for this assignment id. Testing fixes
# Testing polygon holes fix - doesn't work
qaqc.pols <- slot(qaqc.poly, "polygons")
qaqc.pols <- lapply(qaqc.pols, checkPolygonsHoles)
slot(qaqc.poly, "polygons") <- qaqc.pols

#q <- qaqc.poly
setwd("~/eMaphepha_ami/Past_postdoc/Projects/Africa_field_map/Test_data/")
q <- readOGR(dsn = "Polygon_tester.shp", layer = "Polygon_tester")

options(warn = -1)
qo <- gOverlaps(q, byid = T)
qo[which(qo)] <- 1
ql <- list()
for(i in 1:nrow(q)) {
  pol <- q[i, ]
  if(!gIsValid(pol)) {
    print(paste(i, "Crap poly"))
    plot(pol)
    pol.line <- as(pol, "SpatialLines")
    plot(pol.line)
    raster(extent)
    gIsValid(gBuffer(pol, width = 0))
    plot(gBuffer(pol, width = 0), add = T, col = "green")
    plot(gSimplify(pol, tol = 0.5), add = T, border = "green")
    polr <- rasterize(pol.line, )
    crds <- pol@polygons[[1]]@Polygons[[1]]@coords
    crds[-nrow(crds), ]
    
  }
}


sapply(1:ncol(qo), function(x) length(which(qo[x, ])))


qv <- gIsValid(q, byid = T)


qaqc.poly <- gBuffer(qaqc.poly, byid = T, width = 0)
#gBuffer(qaqc.poly, byid = T, width = 0), byid = T)

# Now let's try out idea of fixing geometries
q <- qaqc.poly
pv <- gIsValid(qaqc.poly, byid = T)
p1 <- qaqc.poly[which(pv == FALSE), ]
plist <- lapply(1:length(p1), function(x) p1[x, ])

lapply(plist, function(x) {
  gBuffer(x)
  #p <- slot(slot(x, "polygons")[[1]], "Polygons")
})

p <- slot(slot(p1, "polygons")[[1]], "Polygons")


as(p, "SpatialPolygons")
gBuffer(p[[1]])

coords <- p[[1]]@coords
p[[1]]@coords
plot(coords[duplicated(coords), ])
plot(coords)
tfix <- gBuffer(qaqc.poly[5, ], 0)
coordsfix <- tfix@polygons[[1]]@Polygons[[1]]@coords
plot(tfix)


plot(qaqc.poly[5, ], add = T, col = "blue")

p1 <- qaqc.poly
p2 <- slot(p1, "polygons")
qaqc.pols <- lapply(p2, checkPolygonsHoles)
slot(p1, "polygons") <- qaqc.pols


p = readWKT("POLYGON((0 40,10 50,0 60,40 60,40 100,50 90,60 100,60 60,100 60,90 50,100 40,60 40,60 0,50 10,40 0,40 40,0 40))")
l = readWKT("LINESTRING(0 7,1 6,2 1,3 4,4 1,5 7,6 6,7 4,8 6,9 4)")

par(mfrow=c(2,4))
plot(p);title("Original")
plot(gSimplify(p,tol=10));title("tol: 10")
plot(gSimplify(p,tol=20));title("tol: 20")
plot(gSimplify(p,tol=25));title("tol: 25")

plot(l);title("Original")
plot(gSimplify(l,tol=3));title("tol: 3")
plot(gSimplify(l,tol=5));title("tol: 5")
plot(gSimplify(l,tol=7));title("tol: 7")
par(mfrow=c(1,1))

#LINEARRING Example
l = readWKT("LINEARRING(0 0, 100 100, 100 0, 0 100, 0 0)")
plot(l);title(paste("Valid:",gIsValid(l),"\n",gIsValid(l,reason=TRUE)))

#POLYGON and MULTIPOLYGON Examples
p1 = readWKT("POLYGON ((0 60, 0 0, 60 0, 60 60, 0 60), (20 40, 20 20, 40 20, 40 40, 20 40))")
p2 = readWKT("POLYGON ((0 60, 0 0, 60 0, 60 60, 0 60), (20 40, 20 20, 60 20, 20 40))")
p3 = readWKT("POLYGON ((0 120, 0 0, 140 0, 140 120, 0 120), (100 100, 100 20, 120 20, 120 100, 100 100), (20 100, 20 40, 100 40, 20 100))")

p4 = readWKT("POLYGON ((0 40, 0 0, 40 40, 40 0, 0 40))")
p5 = readWKT("POLYGON ((-10 50, 50 50, 50 -10, -10 -10, -10 50), (0 40, 0 0, 40 40, 40 0, 0 40))")
p6 = readWKT("POLYGON ((0 60, 0 0, 60 0, 60 20, 100 20, 60 20, 60 60, 0 60))")
p7 = readWKT("POLYGON ((40 300, 40 20, 280 20, 280 300, 40 300),(120 240, 80 180, 160 220, 120 240),(220 240, 160 220, 220 160, 220 240),(160 100, 80 180, 100 80, 160 100),(160 100, 220 160, 240 100, 160 100))")
p8 = readWKT("POLYGON ((40 320, 340 320, 340 20, 40 20, 40 320),(100 120, 40 20, 180 100, 100 120),(200 200, 180 100, 240 160, 200 200),(260 260, 240 160, 300 200, 260 260),(300 300, 300 200, 340 320, 300 300))")
p9 = readWKT("MULTIPOLYGON (((20 380, 420 380, 420 20, 20 20, 20 380),(220 340, 180 240, 60 200, 200 180, 340 60, 240 220, 220 340)),((60 200, 340 60, 220 340, 60 200)))")

par(mfrow=c(3,3))
plot(p1,col='black',pbg='white');title(paste("Valid:",gIsValid(p1),"\n",gIsValid(p1,reason=TRUE)))
plot(p2,col='black',pbg='white');title(paste("Valid:",gIsValid(p2),"\n",gIsValid(p2,reason=TRUE)))
plot(p3,col='black',pbg='white');title(paste("Valid:",gIsValid(p3),"\n",gIsValid(p3,reason=TRUE)))
plot(p4,col='black',pbg='white');title(paste("Valid:",gIsValid(p4),"\n",gIsValid(p4,reason=TRUE)))
plot(p5,col='black',pbg='white');title(paste("Valid:",gIsValid(p5),"\n",gIsValid(p5,reason=TRUE)))
plot(p6,col='black',pbg='white');title(paste("Valid:",gIsValid(p6),"\n",gIsValid(p6,reason=TRUE)))
plot(p7,col='black',pbg='white');title(paste("Valid:",gIsValid(p7),"\n",gIsValid(p7,reason=TRUE)))
plot(p8,col='black',pbg='white');title(paste("Valid:",gIsValid(p8),"\n",gIsValid(p8,reason=TRUE)))
plot(p9,col='black',pbg='white');title(paste("Valid:",gIsValid(p9),"\n",gIsValid(p9,reason=TRUE))) 
