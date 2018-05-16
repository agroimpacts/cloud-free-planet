#' Calculate fragmentation accuracy and edge accuracy 
#' @param qaqc.polys qaqc polygons
#' @param user.polys user-map polygons
#' @param buf buffer width for edge accuracy
#' @details This function targets on how the geometry of qaqc polygons are 
#' mapped by user polygons, which should be complementary to the in-grid and 
#' outgrid thematic accuracy. 
#' @import sf
#' @keywords internal
geometric_accuracy <- function(qaqc.polys, user.polys, buf) {
  match_num <- 0 # the number of matched polygons
  acc_edge_sum <- 0 # accumulated edge accuracy
  for(s in 1:nrow(qaqc.polys)) {  # s <- 1
    for(t in 1:nrow(user.polys)) {  # t <- 1
      qaqc_single <- st_geometry(qaqc.polys[s, ])
      user_single <- st_geometry(user.polys[t, ])
      tmp <- st_intersection(qaqc_single, user_single)
      if (length(tmp) > 0) {
        # two critera for matched polygons
        if (as.numeric(st_area(tmp) / st_area(qaqc_single)) > 0.5 &
            as.numeric(st_area(tmp) / st_area(user_single)) > 0.5) {
          match_num <- match_num + 1 
          boundary_qaqc_single <- st_difference(st_buffer(qaqc_single, buf),
                                                st_buffer(qaqc_single, -buf))
          boundary_user_single <- st_difference(st_buffer(user_single, 0.1),
                                                st_buffer(user_single, -0.1))
          # edge accuracy is equal to the intersect length divided by the 
          # perimeter of the qaqc polygon
          intsect <- st_intersection(boundary_qaqc_single, boundary_user_single)
          intsect_ratio <- st_area(intsect) / st_area(boundary_user_single)
          acc_edge_single <- as.numeric(intsect_ratio)
          acc_edge_sum <- acc_edge_sum + acc_edge_single
        }
      }
    }
  }
  if(match_num == 0){
    edge_acc <- 0
    frag_acc <- 0
  }
  else {
    edge_acc <- as.numeric(acc_edge_sum / match_num) 
    # using the number of qaqc not the maximum between qaqc and user is because 
    # extra user polys (false alarms) are factored into thematic accuracy
    frag_acc <- as.numeric(match_num / nrow(qaqc.polys)) 
  }
  # return(list("fragmentaccuracy" = frag_acc, "edgeaccuracy" = edge_acc))
  return(c("fragmentaccuracy" = frag_acc, "edgeaccuracy" = edge_acc))
}