#' Calculates percent agreement between number of fields in qaqc and user kmls
#' @param qaqc_rows vector of count of QAQC rows, or NULL if one doesn't exist
#' @param kml User mapped fields, or NULL if they don't exist
#' @return Score between 0-1
#' @note Rearranges numerator and denominator of equation according to whether 
#' user mapped fields are more or less than QAQC fields
#' @export
countError <- function(qaqc_rows, user_rows) {
  cden <- ifelse(qaqc_rows >= user_rows, qaqc_rows, user_rows)
  cnu1 <- ifelse(qaqc_rows >= user_rows, qaqc_rows, user_rows)
  cnu2 <- ifelse(qaqc_rows >= user_rows, user_rows, qaqc_rows)
  cnterr <- 1 - (cnu1 - cnu2) / cden  # Percent agreement
  return(cnterr)
}

