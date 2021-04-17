This folder includes codes to organize the parcel fabric data from UrbanSim and create animations from heatmap and TAZ mapping. 

# Work flow
## Steps

1. Calculate jobs from non-residential square feet and area per job;

2. Calculate households from dwelling units and vacancy rate;

3. Calculate new developments from the 2020 and 2045 data;

4. Split parcel data by annual step to have yearly and cumulative parcel data;

5. Spatial join between yearly parcel data and TAZ for the Tableau viz;

6. Spatial join between cumulative parcel data and TAZ for heatmaps;

7. Create heatmaps;

8. Map heatmaps and create animations;

9. Map TAZ data and create animations