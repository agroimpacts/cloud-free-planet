#' Calculates mapping accuracy for polygons relative to a "true" set of polygons
#' @param maps Polygons to assess
#' @param truth Polygons against which which accuracy will be assessed
#' @param region: A polygon defining the region in which accuracy is assessed
#' @importFrom sf st_difference st_intersection
#' @return Accuracy measures from user maps
#' @export
mapError <- function(maps, truth, region) {
  if(is.null(truth)) {
    null <- region  # Actual null area is whole region
    tp <- 0  # True positive area is 0
    fp <- maps  # False positive area is all of maps
    fn <- 0  # No false negative area because there are no fields
    tn <- st_difference(null, maps)  # True negative: do poly diff across IDs
  } 
  if(is.null(maps)) {
    null <- st_difference(region, truth) # actual null region in map
    tp <- 0  # No user maps, no true positive
    fp <- 0  # No user maps, no false positives
    fn <- truth  # False negative area is all of truth
    tn <- null  # True negative area is null - user gets credit for this area
  }
  if(!is.null(truth) & !is.null(maps)) {
    null <- st_difference(st_buffer(region, 0), truth)
    tp <- st_intersection(truth, maps)  
    fp <- st_difference(maps, truth)  
    fn <- st_difference(truth, maps)  
    tn <- st_difference(st_buffer(null, 0),maps)
  }
  tflist <- c("tp", "fp", "fn", "tn") 
  areas <- sapply(tflist, function(x) {
    ifelse(!is.null(get(x)) & is.object(get(x)), st_area(get(x)), 0)
  })
  names(areas) <- tflist  
  acc_stats <- accStatsSum(tp = areas["tp"], fp = areas["fp"], 
                           fn = areas["fn"], tn = areas["tn"])
  return(list(acc_stats, tp, fp, fn, tn))
}

