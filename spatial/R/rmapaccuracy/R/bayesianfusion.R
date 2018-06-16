#' Core codes for Bayesian fusion
#' Bayesian fusion creates a heat, a labeled and a conflict map from multiple 
#' user maps based on Bayes theory:
#' Posterior probabability = Prior probability* likelihood
#' Posterior: P(groundtruth = field|user_1, user_2,..., user_n) and
#' P(groundtruth = no field|user_1, user_2,..., user_n) 
#' Prior: P(field) and P(no field)
#' Likelihood: P(user_1, user_2,..., user_n|groundtruth = field) 
#' and P(user_1, user_2,..., user_n|groundtruth = no field) 
#' @param bayes.poly a sf object needs to have  three columns: 
#' lklh_field (P(user_i = field|groundtruth = field)),
#' lklh_nofield(P(user_i = no field|groundtruth = no field)), and geometry
#' P(user_i = field|groundtruth = field) represents the probability that the 
#' user i gives the label of field given the groundtruth is field; 
#' P(user_i = no field|groundtruth = no field) represents the probability that 
#' the user i gives the label of no field given the groundtruth is no field 
#' @param rasterextent the extent for the output
#' @import raster
#' @return A list of a heat map, a labeled map and a conflict map 
#' the heat map is a probability map for field, the label map is a binary field 
#' classification map which is obtained by comparing posterior probability;
#' the conflict map is a map to measure disagreement of user consensus

gcsstr <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
prjstr <- paste0("+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=",
         "25 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs") 

bayesianfusion <- function(bayes.polys, rasterextent){

  # accumulated field area for computing prior probability
  acc_field_area <- 0
  
  # a field likelihood raster of p(user_i|groundtruth = field), meaning 
  # that the probability for a user_i map given that groundtruth is field
  lklh_field_rst <- raster(extent(as(rasterextent, 'Spatial')), 
                           resolution = 0.005/200, crs = gcsstr)
  
  # a no-field likelihood raster of p(user_i = field|groundtruth = no field)
  # meaning the probability for a user_i map given that groundtruth is no field,
  lklh_nofield_rst <- raster(extent(as(rasterextent, 'Spatial')), 
                             resolution = 0.005/200, crs = gcsstr)
  
  # read and process user polygons using a recursive way in order to save memory
  for (t in 1:nrow(bayes.polys)){
    # empty geometry means that user label all map extent as no field
    if (st_is_empty(bayes.polys[t, "geometry"])){
      
      # field likelihood of empty geometry is the probability given that all pixels 
      # are actual field, but user labels them as no field 
      # log(p(user = no field|groundtruth = field)), which is also equal to
      # log(1 - p(user = field|groundtruth = no field))
      val_lklh_field <- rep(1 - as.numeric(bayes.polys[t, 'lklh_field'])[1], 
                            ncol(lklh_field_rst) * nrow(lklh_field_rst))
      lklh_field_rst <- setValues(lklh_field_rst, val_lklh_field)
      
      # no field likelihood of emptry geometry is the probability given that
      # all pixels are a actual no field, user also labels as no field (correctly 
      # classified)
      # log(p(user = no field|groundtruth = no field))
      val_lklh_nofield <- rep(as.numeric(bayes.polys[t, 'lklh_nofield'])[1]
                                         , ncol(lklh_field_rst) * nrow(lklh_field_rst))
      lklh_nofield_rst <- setValues(lklh_nofield_rst, val_lklh_nofield)
    }
    else{
      #calculate accumulated field area
      acc_field_area <- acc_field_area +
        as.numeric(sum(st_area(st_transform(bayes.polys[t, ], crs = prjstr))))
      # lklh_field_rst: a raster of probabilities for user_map i given that all 
      # pixels are actual field
      # polygon = p(user = field|groundtruth = field)
      # background = p(user = no field|groundtruth = field))
      #          = (1 - p(user = field|groundtruth = field)) 
      lklh_field_rst <- fasterize(bayes.polys[t, ], lklh_field_rst, 
                                  field =  "lklh_field", 
                                  background = 1 - 
                                    as.numeric(bayes.polys[t, 'lklh_field'])[1])
      # lklh_nofield_rst: a raster of probabilities for user_map i given that all 
      # pixels are actual no field
      # polygon: p(user = field|groundtruth = no field)
      #         = (1 - p(user = no field|groundtruth = no field))
      # background: p(user = no field|groundtruth = no field))
      lklh_nofield_rst <- fasterize(bayes.polys[t, ],  lklh_nofield_rst, 
                                    field = "lklh_nofield", 
                                    background = 1 - as.numeric
                                    (bayes.polys[t, 'lklh_nofield'])[1])
      lklh_nofield_rst <- calc(lklh_nofield_rst, function(x){1-x})
    }
    if (t == 1){
      # combined log likelihood given an actual field 
      comb_lklh_field_rst <- log(lklh_field_rst)
      # combined log likelihood given an actual no field 
      comb_lklh_nofield_rst <- log(lklh_nofield_rst)
    }
    else{
      # Independence: user maps are independently done, so we can multiple the 
      # combined likelihood without concerning correlation 
      # (the principle of conditional probability)!
      # so, p(user_1, user_2, .., user_n|field) = p(user_1|field)*p(user_2|field)
      #       ...*p(user_n|field)
      # for combined log likelihood: log (p(user_1|field)*p(user_2|field)...) 
      # = log (p(user_1|field) + log (p(user_2|field)+...
      comb_lklh_field_rst <- comb_lklh_field_rst + log(lklh_field_rst)
        
      comb_lklh_nofield_rst <- comb_lklh_nofield_rst + log(lklh_nofield_rst) 
                                  
    }
  } 
  
  # prior probability is the average proportion of field and no field in our grid
  # prior_field <- acc_field_area / (nrow(bayes.polys) * 
                  #as.numeric(st_area(st_transform(rasterextent, crs = prjstr))))
  # prior_nofield <- 1 - prior_field
  prior_field <- 0.5
  prior_nofield <- 0.5
  # if no any field mapped by all users
  if (prior_field == 0){
    label_map <- setValues(lklh_field_rst, rep(0,
                                               ncol(lklh_field_rst) * 
                                                 nrow(lklh_field_rst)))
    heat_map <- setValues(lklh_field_rst, rep(0,
                                               ncol(lklh_field_rst) * 
                                                nrow(lklh_field_rst)))
    conflict_map <- setValues(lklh_field_rst, rep(0,
                                              ncol(lklh_field_rst) * 
                                                nrow(lklh_field_rst)))
  }
  # if all raster extent are mapped as field by all users
  else if (prior_field == 1){
    label_map <- setValues(lklh_field_rst, rep(1,
                                               ncol(lklh_field_rst) * 
                                                 nrow(lklh_field_rst)))
    heat_map <- setValues(lklh_field_rst, rep(1,
                                              ncol(lklh_field_rst) * 
                                                nrow(lklh_field_rst)))
    conflict_map <- setValues(lklh_field_rst, rep(0,
                                                  ncol(lklh_field_rst) * 
                                                    nrow(lklh_field_rst)))
  }
  else{
    # posterior for field: p(field|user_1, user_2, ..., user_n ) = 
    # p(user_1, user_2, ..., user_n|field)* p(field)
    log_posteri_field <- log (prior_field) + comb_lklh_field_rst
    
    # posterior for no field: p(no field|user_1, user_2, ..., user_n ) = 
    # p(user_1, user_2, ..., user_n|no field)* p(no field)
    log_posteri_nofield <- log (prior_nofield) + comb_lklh_nofield_rst
    
    # reclass to get a label map ('1' - field; '0' - no field) by comparing log_posteri_field
    label_map <- reclassify(overlay(log_posteri_field, log_posteri_nofield, 
                                    fun = function(r1, r2){return(r1 - r2)}), 
                            c(-Inf, 0, 0, 0, Inf, 1)) 
    
    heat_map <- overlay (log_posteri_field, log_posteri_nofield, 
                         fun = function(r1, r2){return(exp(r1) /(exp(r1)+exp(r2)))})
    
    
    # conflicts maps is to assign non-field (1-label_map) as heat_map values, and 
    # asssign field as 1-heat_map
    conflict_map <- overlay(heat_map, label_map, fun=function(r1, r2){ r1 *(1-r2)+(1-r1)*r2})
  }

  
  return(list("labelmap" = label_map, "heatmap" = heat_map, "conflictmap" = conflict_map))
    
}
