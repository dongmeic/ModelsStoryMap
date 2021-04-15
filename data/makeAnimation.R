library(animation)
library(stringr)
setwd("T:/Models/StoryMap/UrbanSim")

createAnimation <- function(field = "hh", TAZ=FALSE){
  files = list.files(path = ".", pattern = field, full.names = T)
  if(TAZ){
    keyword = "new_"
  }else{
    keyword = "heatmap_"      
  }
  files = grep(keyword, files, value =TRUE) 
  if(str_detect(files[1], "gif")){
    im.convert(files[-1],output=paste0(keyword, field, ".gif"))
  }else{
    im.convert(files,output=paste0(keyword, field, ".gif"))
  }
}

createAnimation(field = "hh", TAZ=TRUE)