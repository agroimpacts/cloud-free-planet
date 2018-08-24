# Show a grid cell over RasterFoundry images
# uses R's leaflet for display. Requires Rstudio

library(leaflet)
library(dplyr)

# connection
coninfo <- rmapaccuracy::mapper_connect("crowdmapper.org")
gcs <- "+proj=longlat +datum=WGS84 +no_defs"

# enter your id here and fetch the scenes_data for it
idv <- "47948981"
scenes <- tbl(coninfo$con, "scenes_data") %>% filter(cell_id == idv) %>% 
  collect()

# get the cell you need from master_grid and turn it into a polygon
name <- tbl(coninfo$con, "master_grid") %>% filter(id == idv) %>%
  select(id, name, x, y) %>% collect()
gpoly <- rmapaccuracy::point_to_gridpoly(data.table::data.table(name), 
                                         w = 0.005 / 2, gcs, gcs)

# set up display
os <- (scenes %>% filter(season == "OS") %>% filter(row_number() == 1) %>% 
  select(tms_url))$tms_url
gs <- (scenes %>% filter(season == "GS") %>% filter(row_number() == 1) %>% 
         select(tms_url))$tms_url

m <- leaflet() %>% addTiles() %>% setView(name$x, name$y, zoom = 14) %>% 
  addTiles(os, group = "OS") %>% addTiles(gs, group = "GS") %>% 
  addPolygons(data = gpoly, group = "Cell") %>% 
  addLayersControl(overlayGroups = c("Cell", "GS", "OS"),
    options = layersControlOptions(collapsed = FALSE, autoZIndex = FALSE))
m

