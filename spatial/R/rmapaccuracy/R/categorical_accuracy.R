#' Calculate categorical accuracy
categorical_accuracy <- function(qaqc.polys, user.polys){
  categories <- list('TreeCrop', 'AnnualCrop', 'Fallow', 'AgroForestry')
  
  # calculate error for each category
  cat.area <- lapply(1:length(categories), function(x){
    qpoly <- st_union(qaqc.polys %>% dplyr::filter(category == categories[x]))
    upoly <- st_union(user.polys %>% dplyr::filter(category == categories[x])) 
    error.area <- st_area(st_difference(qpoly, upoly))
    correct.area <- st_area(qpoly) + st_area(upoly) - error.area
    c('ErrorArea' = error.area, 'CorrectArea' = correct.area)
  })
  
  # Error and correct area are actually both calculated twice, which will be 
  # cancelled out in the division below
  category.acc <- 1 - sum(as.data.frame(cat.area)["ErrorArea", ])/
    (sum(as.data.frame(cat.area)["ErrorArea", ]) + 
       sum(as.data.frame(cat.area)["CorrectArea", ]))
  return(category.acc)
}