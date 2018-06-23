#' Core codes for Bayesian Model Averaging P(theta|D) = ∑ weight * mapper posterior probability
#' @param bayes.poly a sf object has five columns: 
#' (1)posterior.field and (2)posterior.nofield are mapper posterior probability
#' , which means mappers' opinion for the possibility of field (we set 0 or 1);  
#' (3)max.field.lklh, (4) max.nofield.lklh: the producer's accuracy, which means
#' that given its label as field or no field, the maximum likelihood to be the 
#' mapper i; (5) score
#' Weight = max.nofield.lklh (or max.field.lklh) * score
#' @param rasterextent the extent for the output
#' @param threshold the threshold for P(theta|D) to determine the label of pixels
#' as field or no field
#' @return A list of three rasters--heat map, risk map, and consensus map
#' @export 
# Bayes model avergaing
bayes_model_averaging <- function(bayes.polys, rasterextent, threshold) {

  gcsstr <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
  posterior.field.rst <- raster(extent(as(rasterextent, 'Spatial')), 
                                resolution = 0.005 / 200, crs = gcsstr)
  
  # read and process user polygons using a recursive way in order to save memory
  for (t in 1:nrow(bayes.polys)) {
    # empty geometry means that user label all map extent as no field
    if (st_is_empty(bayes.polys[t, "geometry"])) {
      # p(actual=field|user t=no field)=
      # 1 - p(actual= no field|user t= no field)
      posterior.field.val <- rep((1 - bayes.polys[t,]$posterior.nofield),
                      ncol(posterior.field.rst) * nrow(posterior.field.rst))
      posterior.field.rst <- setValues(posterior.field.rst, posterior.field.val)
      
    }
    else {
      # polygom: p(actual=field|user t=field)
      # bkgd: p(actual= field|user t= no field) = 
      # 1 - p(actual= no field|user t= no field)
      posterior.field.rst <- fasterize(bayes.polys[t, ], posterior.field.rst, 
                                       field = "posterior.field", 
                                       background = 
                                         1 - bayes.polys[t, ]$posterior.nofield)
      }
    user.max.lklh <- fasterize(bayes.polys[t, ], posterior.field.rst, 
                               field =  "max.field.lklh", 
                               background = bayes.polys[t,]$max.nofield.lklh)
    weight <- user.max.lklh * bayes.polys[t,]$prior
    if (t == 1) {
      weight.acc <- weight 
      posterior.acc <- overlay(posterior.field.rst, weight, 
                               fun = function(x, y) (x * y))
      
    } else {
      weight.acc <- weight.acc + weight 
      posterior.acc <- posterior.acc + overlay(posterior.field.rst, weight, 
                                               fun = function(x, y) (x * y)) 
    }
  } 
  
  heat.map <- overlay(posterior.acc, weight.acc,
                      fun = function(x, y) {return(x / y)})
  
  label.map <- reclassify(heat.map, c(-Inf, threshold, 0, threshold, Inf, 1)) 
  
  # risks maps is to assign non-field (1-label.map) as heat.map values, and 
  # asssign field as 1-heat.map
  risk.map <- overlay(heat.map, label.map, 
                      fun=function(r1, r2) {r1 *(1 - r2) + (1 - r1) * r2})
  
  return(list("labelmap" = label.map, "heatmap" = heat.map, 
              "riskmap" = risk.map))
}