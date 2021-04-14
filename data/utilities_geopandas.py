import os, glob
import contextily as ctx
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from matplotlib.ticker import ScalarFormatter
import rasterio
import fiona
from rasterio.plot import show, show_hist
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

path = r'T:\Trans Projects\Model Development\UrbanSim_LandUse\Output\Simulation_47_Final_RTP'
MPObd = gpd.read_file("V:/Data/Transportation/MPO_Bound.shp")
outpath = r'T:\Models\StoryMap\UrbanSim'

class MidpointNormalize(mpl.colors.Normalize):
    def __init__(self, vmin, vmax, midpoint=0, clip=False):
        self.midpoint = midpoint
        mpl.colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        normalized_min = max(0, 1 / 2 * (1 - abs((self.midpoint - self.vmin) / (self.midpoint - self.vmax))))
        normalized_max = min(1, 1 / 2 * (1 + abs((self.vmax - self.midpoint) / (self.midpoint - self.vmin))))
        normalized_mid = 0.5
        x, y = [self.vmin, self.midpoint, self.vmax], [normalized_min, normalized_mid, normalized_max]
        return np.ma.masked_array(np.interp(value, x, y))

def splitData(yrbuilt = 2021, by = 'cum', shpnm = 'parcel_data'):
    shpdata = gpd.read_file(os.path.join(path, 'output', shpnm + '.shp'))
    shpdata = shpdata[shpdata['yrbuilt'] >= 2021]
    if by == 'yearly':
        shpdata = shpdata[shpdata['yrbuilt'] == yrbuilt]
        shpdata.to_file(os.path.join(path, 'output', shpnm + str(yrbuilt) +'.shp'))
        print("Exported yearly {0} in {1}...".format(shpnm, str(yrbuilt)))
    else:
        shpdata = shpdata[shpdata['yrbuilt'] <= yrbuilt]
        shpdata.to_file(os.path.join(path, 'output', shpnm + str(yrbuilt) +'cum.shp'))
        print("Exported cumulative {0} by {1}...".format(shpnm, str(yrbuilt)))

def plotRaster(yrbuilt = 2021, field = "jobs", fieldName = 'Employment', colormap = 'RdBu_r', 
                cellSize = 25, searchRadius = 1000, export = True, changeFileNm = False):
    
    if changeFileNm:
        file = os.path.join(path, 'output', 
                            "KernelD_" + field + "_" + str(yrbuilt) + "_" + str(cellSize) + "_" + str(searchRadius) + ".tif")
    else:
        if yrbuilt == "":
            file = os.path.join(path, 'output', "KernelD_" + field + ".tif")
        else:
            file = os.path.join(path, 'output', "KernelD_" + field + "_" + str(yrbuilt) + ".tif")
    
    src = rasterio.open(file)
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
                     ax=ax, #alpha=0.7,
                     cmap=colormap)
    else:
        image = show(ndata, 
                     transform=src.transform, 
                     ax=ax, 
                     cmap=colormap, 
                     norm=norm)
        
    MPObd.plot(ax=ax, facecolor="none", edgecolor="black", linestyle='--')
    
    ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite, alpha=0.3)
    if yrbuilt == "":
        ax.set_title(fieldName + " Heatmap in Central Lane MPO in 2045", fontsize=50, fontname="Palatino Linotype", 
                  color="grey", loc = 'center')
    else:
        ax.set_title(fieldName + " Heatmap in Central Lane MPO (" + str(yrbuilt) + ")", fontsize=50, fontname="Palatino Linotype", 
                  color="grey", loc = 'center')
    
    if data_ex.min() == 0:
        # use imshow so that we have something to map the colorbar to
        image_hidden = ax.imshow(ndata, 
                                 cmap=colormap)    
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
        if yrbuilt == "":
            plt.savefig(os.path.join(outpath, "heatmap_" + field + ".png"), transparent=True, bbox_inches='tight')
            print("Saved image for " + field + "...")
        else:
            plt.savefig(os.path.join(outpath, "heatmap_" + field + "_" + str(yrbuilt) + ".png"), transparent=True, bbox_inches='tight')
            print("Saved image for " + str(yrbuilt) + "...")
    src.close()
        

