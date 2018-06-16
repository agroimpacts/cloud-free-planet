#' Core codes for Bayesian Model Averaging
#' P(theta|D) = ∑ weight * mapper posterior probability
#' @param bayes.poly a sf object has five columns: 
#' (1)posterior_field and (2)posterior_nofield are mapper posterior probability
#' , which means mappers' opinion for the possibility of field (we set 0 or 1);  
#' (3)max_field_lklh, (4) max_nofield_lklh: the producer's accuracy, which means
#' that given its label as field or no field, the maximum likelihood to be the 
#' mapper i; (5) score
#' Weight = max_nofield_lklh (or max_field_lklh) * score
#' @param rasterextent the extent for the output
#' @param threshold the threshold for P(theta|D) to determine the label of pixels
#' as field or no field

gcsstr <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
prjstr <- paste0("+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=",
                 "25 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs") 


# Bayes model avergaing
BayesModelAveraging <- function(bayes.polys, rasterextent, threshold){
  
  posterior_field_rst <- raster(extent(as(rasterextent, 'Spatial')), 
                        resolution = 0.005/200, crs = gcsstr)
  weight_accumulated <- 0
  # read and process user polygons using a recursive way in order to save memory
  for (t in 1:nrow(bayes.polys)){
    # empty geometry means that user label all map extent as no field
    if (st_is_empty(bayes.polys[t, "geometry"])){
      # p(actual=field|user t=no field)=
      # 1 - p(actual= no field|user t= no field)
      posterior_field_val <- rep((1 - bayes.polys[t,]$posterior_nofield),
                      ncol(posterior_field_rst) * nrow(posterior_field_rst))
      posterior_field_rst <- setValues(posterior_field_rst, posterior_field_val)
      
    }
    else{
      # polygom: p(actual=field|user t=field)
      # bkgd: p(actual= field|user t= no field) = 
      # 1 - p(actual= no field|user t= no field)
      posterior_field_rst <- fasterize(bayes.polys[t, ], posterior_field_rst, 
                               field =  "posterior_field", 
                               background = 1 - bayes.polys[t,]$posterior_nofield)
      }
    user_max_lklh <- fasterize(bayes.polys[t, ], posterior_field_rst, 
                               field =  "max_field_lklh", 
                               background = bayes.polys[t,]$"max_nofield_lklh")
    weight <- user_max_lklh * bayes.polys[t,]$prior
    if (t == 1){
      weight_acc <- weight 
      posterior_acc <- overlay(posterior_field_rst, weight, fun = function(x, y){
        (x * y)
      })
      
    }else{
      weight_acc <- weight_acc + weight 
      posterior_acc <- posterior_acc + overlay(posterior_field_rst, weight, 
                                               fun = function(x, y){ (x * y) }) 
    }
  } 
  
  heat_map <- overlay(posterior_acc, weight_acc,
                    fun = function(x, y){return(x / y)})
  
  label_map <- reclassify(heat_map, 
                          c(-Inf, threshold, 0, threshold, Inf, 1)) 
  
  # risks maps is to assign non-field (1-label_map) as heat_map values, and 
  # asssign field as 1-heat_map
  risk_map <- overlay(heat_map, label_map, fun=function(r1, r2){ r1 *(1-r2)+(1-r1)*r2})
  
  return(list("labelmap" = label_map, "heatmap" = heat_map, "riskmap" = risk_map))
}