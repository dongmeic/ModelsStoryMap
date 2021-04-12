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
        joinFeature = os.path.join(path, 'output', shpnm + str(yrbuilt) +'.shp')
    else:
        joinFeature = os.path.join(path, 'output', shpnm + str(yrbuilt) +'cum.shp')
        
    outFeature = os.path.join(path, "output", shpnm + "_taz_" + str(yrbuilt) + ".shp")
    arcpy.SpatialJoin_analysis(target_features=r"V:\Data\Transportation\TAZ_Bound.shp", 
                           join_features=joinFeature, 
                           out_feature_class=outFeature, 
                           join_operation="JOIN_ONE_TO_ONE", 
                           join_type="KEEP_COMMON", 
                           field_mapping="""TAZ_NUM "TAZ_NUM" true true false 10 Long 0 10 ,First,#,MTAZ16,TAZ_NUM,-1,-1;
                           btype "btype" true true false 18 Double 0 18 ,Mode,#,{0},btype,-1,-1;
                           nsqft "nsqft" true true false 24 Double 15 23 ,Sum,#,{0},nsqft,-1,-1;
                           rsqft "rsqft" true true false 24 Double 15 23 ,Sum,#,{0},rsqft,-1,-1;
                           du "du" true true false 18 Double 0 18 ,Sum,#,{0},du,-1,-1;
                           yrbuilt "yrbuilt" true true false 18 Double 0 18 ,Mode,#,{0},yrbuilt,-1,-1;
                           pundev "pundev" true true false 24 Double 15 23 ,Mean,#,{0},pundev,-1,-1;
                           dev_land "dev_land" true true false 24 Double 15 23 ,Sum,#,{0},dev_land,-1,-1;
                           orsqft "orsqft" true true false 24 Double 15 23 ,Sum,#,{0},orsqft,-1,-1;
                           onrsqft "onrsqft" true true false 24 Double 15 23 ,Sum,#,{0},onrsqft,-1,-1;
                           odu "odu" true true false 24 Double 15 23 ,Sum,#,{0},odu,-1,-1;
                           AreaPerJob "AreaPerJob" true true false 24 Double 15 23,Mean,#,{0},AreaPerJob,-1,-1;
                           isNonRes "isNonRes" true true false 18 Double 0 18,Count,#,{0},isNonRes,-1,-1;
                           jobs "jobs" true true false 24 Double 15 23,Sum,#,{0},jobs,-1,-1;
                           ojobs "ojobs" true true false 24 Double 15 23,Sum,#,{0},ojobs,-1,-1;
                           hh "hh" true true false 24 Double 15 23,Sum,#,{0},hh,-1,-1;
                           ohh "ohh" true true false 24 Double 15 23,Sum,#,{0},ohh,-1,-1""".format(shpnm + "_taz_" + str(yrbuilt)), 
                           match_option="CONTAINS", search_radius="", distance_field_name="")
    fileList = glob.glob(os.path.join(path, "output", shpnm + "_taz_" + str(yrbuilt) + ".*"))
    if fileList != []:
        for filePath in fileList:
            if os.path.exists(filePath):
                os.remove(filePath)
    print("Processed spatial join by " + str(yrbuilt) + "...")

def createHeatmap(yrbuilt = 2021, field = "nnsqft", by = "yearly", cellSize = 100, 
                  changeFileNm = False):
    arcpy.env.extent = MPOBound
    mask = MPOBound
    if by == "yearly":
        inFeature = os.path.join(path, 'output', shpnm + str(yrbuilt) +'.shp')
    else:
        inFeature = os.path.join(path, 'output', shpnm + str(yrbuilt) +'cum.shp')
    
    arcpy.FeatureToPoint_management(in_features=inFeature, 
                                out_feature_class="dataCentroids", point_location="INSIDE")
    if changeFileNm:
        outRaster = os.path.join(path, 'output', "KernelD_" + field + "_" + str(yrbuilt) + "_" + str(cellSize) + ".tif")
    else:
        outRaster = os.path.join(path, 'output', "KernelD_" + field + "_" + str(yrbuilt) + ".tif")
    with arcpy.EnvManager(mask=MPOBound):
            arcpy.gp.KernelDensity_sa("newDevCentroid", field, 
                          outRaster,
                          cellSize,"", "SQUARE_KILOMETERS", "DENSITIES", "GEODESIC")
