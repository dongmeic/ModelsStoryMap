import os, glob
import contextily as ctx
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab as plot
import matplotlib.ticker as tick
from matplotlib.ticker import ScalarFormatter
import rasterio
import fiona
from rasterio.plot import show, show_hist
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import colors


path = r'T:\Trans Projects\Model Development\UrbanSim_LandUse\Output\Simulation_47_Final_RTP'
TAZ = gpd.read_file("V:/Data/Transportation/TAZ_Bound.shp")
MPObd = gpd.read_file("V:/Data/Transportation/MPO_Bound.shp")
outpath = r'T:\Models\StoryMap\UrbanSim'


df = pd.read_csv('../../RTP/analysis/building_types.csv')
# get non-residential building types
btypes = df[df['is_non_residential']]['building_type_id'].unique()
# get residential building tpyes
ndf = df[df['is_residential']]
res_btypes = ndf[~ndf['is_non_residential']]['building_type_id'].unique()
bsqft_per_job = pd.read_csv('../../RTP/analysis/bsqft_per_job.csv')

def compute_jobs(x, sqft, area):
    return sqft / area if x else None

# apply the area_per_job function on the btype field
def area_per_job(x):
    if x[1:-2] == '':
        area_per_job = None
        isNonRes = False
    else:
        if len(x[1:-2].split(', ')) == 1:
            a = x[1:-2].split(', ')
            if int(a[0]) in btypes:            
                area_per_job = bsqft_per_job.loc[bsqft_per_job.building_type_id == int(a[0]), 'area_per_job'].values[0]
                isNonRes = True
            elif int(a[0]) in res_btypes:
                if int(a[0]) in bsqft_per_job.building_type_id:
                    area_per_job = bsqft_per_job.loc[bsqft_per_job.building_type_id == int(a[0]), 'area_per_job'].values[0]
                else:
                    area_per_job = None
                isNonRes = False
            else:
                area_per_job = None
                isNonRes = False
        else:
            a = x[1:-1].split(', ')
            b = [int(btype) for btype in a]
            btypeList = [btype for btype in b if btype in btypes]
            res_btypeList = [btype for btype in b if btype in res_btypes]
            if btypeList == []:
                area_per_job = bsqft_per_job.loc[bsqft_per_job.building_type_id.isin(res_btypeList), 'area_per_job'].mean()
                isNonRes = False
            else:
                area_per_job = bsqft_per_job.loc[bsqft_per_job.building_type_id.isin(btypeList), 'area_per_job'].mean()
                isNonRes = True
    return(area_per_job, isNonRes)

class ScalarFormatterForceFormat(ScalarFormatter):
    def _set_format(self):  # Override function that finds format to use.
        self.format = "%1.1f"  # Give format here

def getMinMax(field = 'njobs'):
    vmins = []
    vmaxs = []
    for yrbuilt in range(2021, 2046, 1):
        file = os.path.join(path, 'output', "KernelD_" + field + "_" + str(yrbuilt) + ".tif")
        src = rasterio.open(file)
        data = src.read(1)
        data_ex = data[data != data.min()]
        vmins.append(data_ex.min())
        vmaxs.append(data.max())
        src.close()
    return min(vmins), max(vmaxs)
        
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

def plotRaster(yrbuilt = 2021, field = "njobs", fieldName = 'Employment', colormap = 'RdYlBu_r', 
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
    norm = colors.TwoSlopeNorm(vmin=getMinMax(field)[0], vcenter=0, vmax=getMinMax(field)[1])
    
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
        ax.set_title("Heatmap on New {0} in Central Lane MPO by {1}".format(fieldName, str(yrbuilt)), 
                     fontsize=50, fontname="Palatino Linotype", color="grey", loc = 'center')
    
    if data_ex.min() == 0:
        # use imshow so that we have something to map the colorbar to
        image_hidden = ax.imshow(ndata, 
                                 cmap=colormap)    
    else:
        image_hidden = ax.imshow(ndata, 
                                 cmap=colormap, 
                                 norm=norm)

    fmt = mpl.ticker.ScalarFormatter(useMathText=True)
    #fmt = ScalarFormatterForceFormat()
    fmt.set_powerlimits((0, 0))
    cbar = plt.colorbar(image_hidden, format=fmt, ax=ax, cax=cax, orientation="horizontal")
    ax.axis("off");
    
    if export:
        if yrbuilt == "":
            plt.savefig(os.path.join(outpath, "heatmap_" + field + ".png"), transparent=True, bbox_inches='tight')
            print("Saved image for " + field + "...")
        else:
            plt.savefig(os.path.join(outpath, "heatmap_" + field + "_" + str(yrbuilt) + ".png"), transparent=True, bbox_inches='tight')
            print("Saved image for " + str(yrbuilt) + "...")
    src.close()
    
def mapTAZdata(yrbuilt = 2021, field = 'jobs', scheme ='naturalbreaks', export = True):
    newDevTaz = gpd.read_file(os.path.join(path, "output", "parcel_data_taz_" + str(yrbuilt) + ".shp"))
    
    if field == 'jobs':
        fieldName = 'Employment'
    elif field == 'hh':
        fieldName = 'Households'
    else:
        print("Need fieldName!")

    min_val, max_val = 0.3,1.0
    n = 10
    orig_cmap = plt.cm.YlOrRd
    colors = orig_cmap(np.linspace(min_val, max_val, n))
    cmap = mpl.colors.LinearSegmentedColormap.from_list("mycmap", colors)
        
    fig, ax = plt.subplots(figsize=(28, 24))
    TAZ.plot(ax=ax, facecolor="none", edgecolor="none", alpha=.3, linestyle='--')
    
    params = {'legend.fontsize': 25, 'legend.handlelength': 2}
    plot.rcParams.update(params)
    newDevTaz.plot(ax=ax, column=field, cmap=cmap, edgecolor='none',
                       scheme =scheme, alpha=.8,
                       legend=True, legend_kwds={"fmt": "{:.0f}"})

    MPObd.plot(ax=ax, facecolor="none", edgecolor="black", linestyle='--')
    ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite)
    plt.title("New {0} in Central Lane MPO by {1}".format(fieldName, str(yrbuilt)), fontsize=50, fontname="Palatino Linotype", 
          color="grey", loc = 'center')
    ax.ticklabel_format(style='sci')
    ax.axis("off");

    if export:
        plt.savefig(os.path.join(outpath, "new_" + field + "_" + str(yrbuilt) + ".png"), transparent=True, bbox_inches='tight')
        print("Saved image for " + str(yrbuilt) + "...")