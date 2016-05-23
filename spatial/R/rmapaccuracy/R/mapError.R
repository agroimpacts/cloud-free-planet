#' Calculates mapping accuracy for polygons relative to a "true" set of polygons
#' @param maps Polygons to assess
#' @param truth Polygons against which which accuracy will be assessed
#' @param region: A polygon defining the region in which accuracy is assessed
#' @return Accuracy measures from user maps
#' @importFrom rgeos gDifference gIntersection
#' @export
mapError <- function(maps, truth, region) {
  if(is.null(truth)) {
    null <- region  # Actual null area is whole region
    tp <- 0  # True positive area is 0
    fp <- maps  # False positive area is all of maps
    fn <- 0  # No false negative area because there are no fields
    tn <- gDifference(spgeom1 = null, spgeom2 = maps, byid = FALSE)  # FN 
  } 
  if(is.null(maps)) {
    null <- gDifference(spgeom1 = region, spgeom2 = truth, 
                               byid = FALSE) # actual null region in map
    tp <- 0  # No user maps, no true positive
    fp <- 0  # No user maps, no false positives
    fn <- truth  # False negative area is all of truth
    tn <- null  # True negative area is null - user gets credit for this area
  }
  if(!is.null(truth) & !is.null(maps)) {
    null <- gDifference(spgeom1 = gBuffer(region, width = 0), spgeom2 = truth, 
                        byid = TRUE)
    tp <- gIntersection(spgeom1 = truth, spgeom2 = maps, byid = TRUE)  
    fp <- gDifference(spgeom1 = maps, spgeom2 = truth, byid = TRUE)  
    fn <- gDifference(spgeom1 = truth, spgeom2 = maps, byid = TRUE)  
    tn <- gDifference(spgeom1 = gBuffer(null, width = 0), spgeom2 = maps, 
                      byid = TRUE)
  }
  tflist <- c("tp", "fp", "fn", "tn") 
  areas <- sapply(tflist, function(x) {
    ifelse(!is.null(get(x)) & is.object(get(x)), rgeos::gArea(get(x)), 0)
  })
  names(areas) <- tflist  
  acc_stats <- accStatsSum(tp = areas["tp"], fp = areas["fp"], 
                           fn = areas["fn"], tn = areas["tn"])
  return(list(acc_stats, tp, fp, fn, tn))
}

