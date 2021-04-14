library(animation)
library(magick)
setwd("T:/Models/StoryMap/UrbanSim")

#field <- "hh"
im.convert(list.files(path = ".", pattern = "hh", full.names = T),
           output=paste0("heatmap_", field, ".gif"))

list.files(path = ".", pattern = "hh", full.names = T)[-1]
