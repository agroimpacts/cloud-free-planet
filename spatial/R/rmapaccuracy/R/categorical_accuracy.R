#' Calculate categorical accuracy
#' @param qaqc.polys qaqc polygons 
#' @param user.polys user polygons (excluding polygons that users are unsure 
#' about field or no field)
#' @param cate.code the category codes reads from database
#' @details categorical accuracy = field area with correct category labels 
#' divided by field area with correct field/no-field labels  
#' @return categorical accuracy
#' @import dplyr
#' 
categorical_accuracy <- function(qaqc.polys, user.polys, cate.code){
  
  # calculate error for each category
  cat.area <- lapply(1:length(cate.code), function(x){
    qpoly <- st_union(qaqc.polys %>% dplyr::filter(category == cate.code[x]))
    
    # the focused polygons that has the same label as the above qaqc polygon 
    upoly.focus <- st_union(user.polys %>% 
                              dplyr::filter(category == cate.code[x]))
    
    # compute correct area intersected region
    categ.correct <- st_intersection(qpoly, upoly.focus)
    correct.area <- ifelse(!is.null(categ.correct) & is.object(categ.correct) 
                           & length(categ.correct) > 0, st_area(categ.correct),
                           0)
    
    c('CorrectArea' = correct.area)
  })
  
  cat.area.rbind <- do.call(rbind,cat.area)
  
  # focus on only general field intersect area, which is counted as corrected
  # in in-grid and out-grid region. 
  field.intersect <- st_intersection(st_union(qaqc.polys), 
                                                  st_union(user.polys))
  
  # calculate the categorical error within accurate general field 
  # (field.intersect.area ) to avoid redundant error calculation
  if(!is.null(field.intersect)& is.object(field.intersect) 
                & length(field.intersect) > 0){
    category.acc <- sum(cat.area.rbind[, "CorrectArea"]) /
                          as.numeric(st_area(field.intersect))
  } 
  else{
    category.acc <- 0
  }
  
  return(category.acc)
}