import os, glob
import contextily as ctx
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from matplotlib.ticker import ScalarFormatter
import rasterio
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

path = r'T:\Trans Projects\Model Development\UrbanSim_LandUse\Output\Simulation_47_Final_RTP'

def exportNewDevData(yrbuilt = 2021, by = 'yearly', step = 1):
    newDev = gpd.read_file(os.path.join(path, 'new_developments.shp'))
    for yrbuilt in range(2021, 2046, step):
        if by == 'yearly':
            newDevAnn = newDev[newDev['yrbuilt'] == yrbuilt]
            newDevAnn.to_file(os.path.join(path, 'output', 'newDevAnn'+ str(yrbuilt) +'.shp'))
            print("Exported yearly " + str(yrbuilt) + "...")
        else:
            newDevAnn = newDev[newDev['yrbuilt'] <= yrbuilt]
            newDevAnn.to_file(os.path.join(path, 'output', 'newDevAnn'+ str(yrbuilt) +'cum.shp'))
            print("Exported cumulative data by " + str(yrbuilt) + "...")

def plotRaster(yrbuilt = 2021, field = "nnsqft", fieldName = 'New Non-res SQFT', colormap = 'RdBu_r', 
                export = True):
    file = os.path.join(path, 'output', "KernelD_" + field + "_" + str(yrbuilt) + ".tif")
    src = rasterio.open(file, mode="r+")
    fig, ax = plt.subplots(figsize=(28, 24))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad="2%")
    
    # plot on the same axis with rio.plot.show
    data = src.read(1)
    ndata = np.where(data == data.min(), np.nan, data)

    data_ex = data[data != data.min()]
    norm = MidpointNormalize(vmin = data_ex.min(), vmax = data.max(), midpoint=0)
    
    if data_ex.min() == 0: 
        image = show(ndata, 
                     transform=src.transform, 
                     ax=ax, 
                     cmap="Reds")
    else:
        image = show(ndata, 
                     transform=src.transform, 
                     ax=ax, 
                     cmap=colormap, 
                     norm=norm)
        
    MPObd.plot(ax=ax, facecolor="none", edgecolor="black", linestyle='--')
    
    ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite, alpha=0.3)
    ax.set_title(fieldName + " Heatmap in Central Lane MPO (" + str(yrbuilt) + ")", fontsize=50, fontname="Palatino Linotype", 
                  color="grey", loc = 'center')
    
    if yrbuilt in [2044, 2045] and field == "nnsqft":
        # use imshow so that we have something to map the colorbar to
        image_hidden = ax.imshow(ndata, 
                                 cmap="Reds")    
    else:
        image_hidden = ax.imshow(ndata, 
                                 cmap=colormap, 
                                 norm=norm)

    fmt = mpl.ticker.ScalarFormatter(useMathText=True)
    fmt.set_powerlimits((0, 0))
    cbar = plt.colorbar(image_hidden, format=fmt, ax=ax, cax=cax, orientation="horizontal")

    mpl.rcParams.update({'font.size': 20})

    ax.axis("off");
    if export:
        plt.savefig(os.path.join(outpath, "heatmap_" + field + "_" + str(yrbuilt) + ".png"), transparent=True, bbox_inches='tight')
        print("Saved image for " + str(yrbuilt) + "...")
    src.close()
        

