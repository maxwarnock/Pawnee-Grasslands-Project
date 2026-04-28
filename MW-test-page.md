---
layout: default
title: Test
---

### Pawnee National Grasslands Property Boundary Data

This project relies on publically available property boundary data. The Pawnee National Grasslands are located in Weld County, and we used Weld County's GIS Hub to download parcel level vector data. This GeoDataFrame includes an attribute table with information about property ownership, address, and polygon geometry for each parcel. From this, we are able to select federal, state, and privately owned land and map these different property types. 

#### Grassland Master Boundary
The Pawnee National Grasslands include a mix of federal, state, and privately owned land. After researching online, we were unable to find a shapefile for the master boundary (official extent) of the grasslands. A resource for the master boundary can be found here [Pawnee National Grasslands FSBaseMap](https://usfs.hub.arcgis.com/maps/9b7e938de9fc45aeaea4bfe4b8868ec6/explore). However, this resource provides the file as a "Vector Tile Service" which is not editable. We needed an editable shapefile of the master boundary in order to clip all of our downstream data to the study area. Therefore, using the resource above, we traced exact boundary in ArcGIS Pro to create an editable shapefile. 

<embed type="text/html" src="figures/boundary_figures/pawnee_boundary_plot.html" width="600">

**Figure #:** This map shows the boundaries of the Pawnee National Grasslands. The master boundary shows the official extent of the Grasslands which includes a mix of federal, state, and privately owned property. The transparent areas are private property. The map shows the fragmented nature of land ownership on the grasslands. Notice the higher degre of contiguity of federally owned land on the western area of the grasslands.

### Subsetting to the Western Half of the Grasslands
In order to narrow our initial study area and potentially identify higher impact land swaps, we are focusing our study on the western half of the Grasslands. This area already has a higher degree of contiguity of federally owned land, and provides the potential to improve this further. 

<embed type="text/html" src="figures/boundary_figures/west_pawnee_boundary_plot.html" width="600">

**Figure #:** This map shows parcel data for the western Pawnee National Grasslands. Private property boundaries are included in white. 

The method for downloading and preparing the boundary data can be found in the 'boundaries.ipynb' in our [repository](https://github.com/maxwarnock/Pawnee-Grasslands-Project/tree/main/code). 
