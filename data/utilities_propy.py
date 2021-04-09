import arcpy, os, glob

ExtensionName = 'Spatial'
if arcpy.CheckExtension(ExtensionName) == "Available":
        arcpy.CheckOutExtension(ExtensionName)
        
arcpy.env.workspace = r'T:\Models\StoryMap\UrbanSim\UrbanSim.gdb'
arcpy.env.overwriteOutput = True
MPOBound = "V:/Data/Transportation/MPO_Bound.shp"
arcpy.env.extent = MPOBound
mask = MPOBound

path = r'T:\Trans Projects\Model Development\UrbanSim_LandUse\Output\Simulation_47_Final_RTP'

def cleanFiles(path = path, name_pattern = "KernelD_", extension = "tif"):
    fileList = glob.glob(os.path.join(path, 'output', '*.{0}'.format(extension)), recursive=True)
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)
    print("cleaned!")
    
def spatialJoin(yrbuilt = 2021, by = 'yearly'):
    if by == 'yearly':
        joinFeature = os.path.join(path, 'output', 'newDevAnn'+ str(yrbuilt) +'.shp')
    else:
        joinFeature = os.path.join(path, 'output', 'newDevAnn'+ str(yrbuilt) +'cum.shp')
        
    outFeature = os.path.join(path, "output", "newDev_taz_" + str(yrbuilt) + ".shp")
    arcpy.SpatialJoin_analysis(target_features=r"V:\Data\Transportation\MTAZ16.shp", 
                           join_features=joinFeature, 
                           out_feature_class=outFeature, 
                           join_operation="JOIN_ONE_TO_ONE", 
                           join_type="KEEP_COMMON", 
                           field_mapping="""TAZ_NUM "TAZ_NUM" true true false 10 Long 0 10 ,First,#,MTAZ16,TAZ_NUM,-1,-1;
                           btype "btype" true true false 18 Double 0 18 ,Mode,#,newDevAnn,btype,-1,-1;
                           nsqft "nsqft" true true false 24 Double 15 23 ,Sum,#,newDevAnn,nsqft,-1,-1;
                           rsqft "rsqft" true true false 24 Double 15 23 ,Sum,#,newDevAnn,rsqft,-1,-1;
                           du "du" true true false 18 Double 0 18 ,Sum,#,newDevAnn,du,-1,-1;
                           yrbuilt "yrbuilt" true true false 18 Double 0 18 ,First,#,newDevAnn,yrbuilt,-1,-1;
                           pundev "pundev" true true false 24 Double 15 23 ,Sum,#,newDevAnn,pundev,-1,-1;
                           dev_land "dev_land" true true false 24 Double 15 23 ,Sum,#,newDevAnn,dev_land,-1,-1;
                           orsqft "orsqft" true true false 24 Double 15 23 ,Sum,#,newDevAnn,orsqft,-1,-1;
                           onrsqft "onrsqft" true true false 24 Double 15 23 ,Sum,#,newDevAnn,onrsqft,-1,-1;
                           odu "odu" true true false 24 Double 15 23 ,Sum,#,newDevAnn,odu,-1,-1;
                           ndu "ndu" true true false 5 Long 0 5 ,Sum,#,newDevAnn,ndu,-1,-1;
                           nnsqft "nnsqft" true true false 19 Double 0 0 ,Sum,#,newDevAnn,nnsqft,-1,-1""", 
                           match_option="CONTAINS", search_radius="", distance_field_name="")
    fileList = glob.glob(os.path.join(path, "output", "newDev_taz_" + str(yrbuilt) + ".*"))
    if fileList != []:
        for filePath in fileList:
            if os.path.exists(filePath):
                os.remove(filePath)
    print("Processed spatial join for the new dev data by " + str(yrbuilt) + "...")

def createHeatmap(yrbuilt = 2021, field = "nnsqft", by = "yearly"):
    if by == "yearly":
        inFeature = os.path.join(path, 'output', 'newDevAnn' + str(yrbuilt) +'.shp')
    else:
        inFeature = os.path.join(path, 'output', 'newDevAnn' + str(yrbuilt) +'cum.shp')
    
    prjFileName = "newDevAnn" + str(yrbuilt) + "prj"
    fileList = glob.glob(os.path.join(path, "output", prjFileName + ".*"))
    if fileList != []:
        for filePath in fileList:
            if os.path.exists(filePath):
                os.remove(filePath)
    
    prjFeature = os.path.join(path, "output", prjFileName + ".shp")
    arcpy.management.Project(inFeature, prjFeature, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "NAD_1983_HARN_To_WGS_1984_2", "PROJCS['NAD83_HARN_Oregon_South_ft',GEOGCS['GCS_NAD83_HARN',DATUM['D_North_American_1983_HARN',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',4921259.843],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-120.5],PARAMETER['Standard_Parallel_1',42.3333333333333],PARAMETER['Standard_Parallel_2',44.0],PARAMETER['Latitude_Of_Origin',41.6666666666667],UNIT['foot',0.3048]]", "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")
    
    arcpy.FeatureToPoint_management(in_features=prjFeature, 
                                out_feature_class="newDevCentroid", point_location="INSIDE")
   
    with arcpy.EnvManager(mask=MPOBound):
            arcpy.gp.KernelDensity_sa("newDevCentroid", field, 
                          os.path.join(path, 'output', "KernelD_" + field + "_" + str(yrbuilt) + ".tif"),
                          "100","", "SQUARE_KILOMETERS", "DENSITIES", "GEODESIC")
