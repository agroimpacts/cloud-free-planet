gcsstr <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
prjstr <- paste0("+proj=aea +lat_1=20 +lat_2=-23 +lat_0=0 +lon_0=",
                 "25 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs") 

heatmapcreation <- function(bayes.polys, rasterextent){
  
  heatmap_rst <- raster(extent(as(rasterextent, 'Spatial')), 
                           resolution = 0.005/200, crs = gcsstr)
  score_accumulated <- 0
  # read and process user polygons using a recursive way in order to save memory
  for (t in 1:nrow(bayes.polys)){
    # empty geometry means that user label all map extent as no field
    if (st_is_empty(bayes.polys[t, "geometry"])){
      heatvalue <- rep(0, ncol(heatmap_rst) * nrow(heatmap_rst))
      heatmap_rst <- setValues(heatmap_rst, heatvalue)
      
    }
    else{
      heatmap_rst <- fasterize(bayes.polys[t, ], heatmap_rst, 
                                  field =  "score", 
                                  background = 0)
    }
    
    if (t == 1){
      comb_heatmap_rst <- heatmap_rst
      score_accumulated <- as.numeric(bayes.polys[t,]$score)
    }
    else{
      comb_heatmap_rst <- comb_heatmap_rst+ heatmap_rst
      score_accumulated <- score_accumulated + 
                            as.numeric(bayes.polys[t,]$score)
    }
  } 
  
  heat_map <- calc (comb_heatmap_rst, 
                         fun = function(r1){return(r1 / score_accumulated)})
    
  return (heat_map)
}