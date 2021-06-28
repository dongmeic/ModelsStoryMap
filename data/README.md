This folder includes codes to organize the parcel fabric data from UrbanSim and create animations from heatmap and TAZ mapping, using single-year and cumulative data. The steps are run in Jupyter Notebook with two python virtural environments - with geopandas or arcpy. The Jupyter Notebooks are numbered by the order of data exploration and visualization. The calculation of jobs is shared in the [network analysis process](https://github.com/dongmeic/RTP/tree/main/analysis). 

# Steps

1. Calculate jobs from non-residential square feet and area per job;

The data set `parcel_fabric.shp` is used to calculate number of jobs and households. The data set `new_developments.shp` is a subset of `parcel_fabric.shp`. The variables are explained as below:

btype:  building_type_id of new development

nsqft:  non-residential square footage

rsqft:  residential square footage

du:     residential units

yrbuilt:  year built

lpid:  parcel_id

pundev:  proportion_undevelopable of parcel

dev_land:  developable square footage of parcel

orsqft:  residential square footage of demolished building(s)

onrsqft:  non-residential square footage of demolished building(s)

odu:  residential units of demolished building(s)

dua:  units per acre of new development

nrfar:  non-residential FAR of new development

2. Calculate households from dwelling units and vacancy rate;

3. Calculate new developments from the 2020 and 2045 data;

4. Split parcel data by annual step to have yearly and cumulative parcel data;

5. Spatial join between yearly parcel data and TAZ and append yearly TAZ data for the Tableau viz;

6. Spatial join between cumulative parcel data and TAZ for TAZ maps;

7. Create heatmaps;

8. Map heatmaps and create animations;

9. Map TAZ data and create animations.