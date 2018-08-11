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
    # the rest polygons 
    upoly.rest <- st_union(user.polys %>% 
                             dplyr::filter(category != cate.code[x])) 
    
    # only compute the errors between two field categories, and ignore the errors
    # that are between field and no field
    categ.error <- st_intersection(qpoly, upoly.rest)
    error.area <- ifelse(!is.null(categ.error) & is.object(categ.error) 
                         & length(categ.error) > 0, st_area(categ.error), 0)
    
    categ.correct <- st_intersection(qpoly, upoly.focus)
    correct.area <- ifelse(!is.null(categ.correct) & is.object(categ.correct) 
                           & length(categ.correct) > 0, st_area(categ.correct),
                           0)
    
    c('ErrorArea' = error.area, 'CorrectArea' = correct.area)
  })
  
  cat.area.rbind <- do.call(rbind,cat.area)
  
  # Error and correct area are actually both calculated twice, which will be 
  # cancelled out in the division below
  category.acc <- 1 - sum(cat.area.rbind[, "ErrorArea"]) /
    sum(cat.area.rbind)
  return(category.acc)
}