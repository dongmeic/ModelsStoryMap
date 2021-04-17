import arcpy, os, glob

ExtensionName = 'Spatial'
if arcpy.CheckExtension(ExtensionName) == "Available":
        arcpy.CheckOutExtension(ExtensionName)
        
arcpy.env.workspace = r'T:\Models\StoryMap\UrbanSim\UrbanSim.gdb'
arcpy.env.overwriteOutput = True
MPOBound = "V:/Data/Transportation/MPO_Bound.shp"

path = r'T:\Trans Projects\Model Development\UrbanSim_LandUse\Output\Simulation_47_Final_RTP'

def cleanFiles(path = path, name_pattern = "KernelD_", extension = "tif"):
    fileList = glob.glob(os.path.join(path, 'output', '*.{0}'.format(extension)), recursive=True)
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)
    print("cleaned!")   
    
def spatialJoin(yrbuilt = 2021, shpnm = 'parcel_data', by = 'cum'):
    if by == 'yearly':
        joinFeatureNm = shpnm + str(yrbuilt)
    else:
        joinFeatureNm = shpnm + str(yrbuilt) + "cum"
        
    joinFeature = os.path.join(path, 'output', joinFeatureNm +'.shp')
    outFeatureNm = shpnm + "_taz_" + str(yrbuilt)
    outFeature = os.path.join(path, "output", outFeatureNm + ".shp")
    
    fileList = glob.glob(os.path.join(path, "output", outFeatureNm + ".*"))
    if fileList != []:
        for filePath in fileList:
            if os.path.exists(filePath):
                os.remove(filePath)
                
    arcpy.analysis.SpatialJoin(target_features=r"V:\Data\Transportation\TAZ_Bound.shp", 
                               join_features=joinFeature, 
                               out_feature_class=outFeature,
                               join_operation="JOIN_ONE_TO_ONE", 
                               join_type="KEEP_COMMON", 
                               field_mapping='TAZ_NUM "TAZ_NUM" true true false 18 Double 0 18,First,#,TAZ_Bound,TAZ_NUM,-1,-1;btype "btype" true true false 80 Text 0 0,First,#,{0},btype,0,80;nrsqft "nrsqft" true true false 24 Double 15 23,Sum,#,{0},nrsqft,-1,-1;rsqft "rsqft" true true false 24 Double 15 23,Sum,#,{0},rsqft,-1,-1;du "du" true true false 24 Double 15 23,Sum,#,{0},du,-1,-1;yrbuilt "yrbuilt" true true false 18 Double 0 18,Last,#,{0},yrbuilt,-1,-1;pundev "pundev" true true false 24 Double 15 23,Mean,#,{0},pundev,-1,-1;dev_land "dev_land" true true false 24 Double 15 23,Sum,#,{0},dev_land,-1,-1;developed "developed" true true false 18 Double 0 18,Sum,#,{0},developed,-1,-1;obtype "obtype" true true false 80 Text 0 0,First,#,{0},obtype,0,80;orsqft "orsqft" true true false 24 Double 15 23,Sum,#,{0},orsqft,-1,-1;onrsqft "onrsqft" true true false 24 Double 15 23,Sum,#,{0},onrsqft,-1,-1;odu "odu" true true false 24 Double 15 23,Sum,#,{0},odu,-1,-1;rezoned "rezoned" true true false 18 Double 0 18,Sum,#,{0},rezoned,-1,-1;annexed "annexed" true true false 18 Double 0 18,Sum,#,{0},annexed,-1,-1;AreaPerJob "AreaPerJob" true true false 24 Double 15 23,Mean,#,{0},AreaPerJob,-1,-1;isNonRes "isNonRes" true true false 18 Double 0 18,Sum,#,{0},isNonRes,-1,-1;jobs "jobs" true true false 24 Double 15 23,Sum,#,{0},jobs,-1,-1;ojobs "ojobs" true true false 24 Double 15 23,Sum,#,{0},ojobs,-1,-1;njobs "njobs" true true false 24 Double 15 23,Sum,#,{0},njobs,-1,-1;hh "hh" true true false 24 Double 15 23,Sum,#,{0},hh,-1,-1;ohh "ohh" true true false 24 Double 15 23,Sum,#,{0},ohh,-1,-1;nhh "nhh" true true false 24 Double 15 23,Sum,#,{0},nhh,-1,-1'.format(joinFeatureNm), 
                               match_option="CONTAINS", search_radius="", distance_field_name="")
    
    print("Processed spatial join for {0} by {1}...".format(shpnm, str(yrbuilt)))

def createHeatmap(yrbuilt = 2021, shpnm = 'parcel_data', field = "jobs", by = "cum", cellSize = 25, 
                  searchRadius = 1000, changeFileNm = False):
    arcpy.env.extent = MPOBound
    mask = MPOBound
    if by == "yearly":
        inFeature = os.path.join(path, 'output', shpnm + str(yrbuilt) +'.shp')
    else:
        if yrbuilt == "":
            inFeature = os.path.join(path, 'output', shpnm +'.shp')
        else:
            inFeature = os.path.join(path, 'output', shpnm + str(yrbuilt) +'cum.shp')
    
    arcpy.FeatureToPoint_management(in_features=inFeature, 
                                out_feature_class="dataCentroids", point_location="INSIDE")
    if changeFileNm:
        outRaster = os.path.join(path, 'output', 
                                 "KernelD_" + field + "_" + str(yrbuilt) + "_" + str(cellSize) + "_" + str(searchRadius) + ".tif")
    else:
        if yrbuilt == "":
            outRaster = os.path.join(path, 'output', "KernelD_" + field + ".tif")
        else:
            outRaster = os.path.join(path, 'output', "KernelD_" + field + "_" + str(yrbuilt) + ".tif")
    with arcpy.EnvManager(mask=MPOBound):
            arcpy.gp.KernelDensity_sa("dataCentroids", field, outRaster, cellSize, searchRadius, 
                                      "SQUARE_KILOMETERS", "DENSITIES", "GEODESIC")
    #output_raster = arcpy.sa.RasterCalculator('Int(outRaster)') 
    #output_raster.save(outRaster)
    
    if yrbuilt == "":
        print("Created the heatmap for {0}".format(field))
    else:
        print("Created the heatmap for {0} in {1}".format(field, yrbuilt))
