---
layout: default
title: Test
---

# Pawnee National Grasslands Property Boundary Data

This project relies on publically available property boundary data. The Pawnee National Grasslands are located in Weld County, and we used Weld County's GIS Hub to download parcel level vector data. This GeoDataFrame includes an attribute table with information about property ownership, address, and polygon geometry for each parcel. From this, we are able to select federal, state, and privately owned land and map these different property types. 

#### Grassland Master Boundary
The Pawnee National Grasslands include a mix of federal, state, and privately owned land. After researching online, we were unable to find a shapefile for the master boundary (official extent) of the grasslands. A resource for the master boundary can be found here [Pawnee National Grasslands FSBaseMap](https://usfs.hub.arcgis.com/maps/9b7e938de9fc45aeaea4bfe4b8868ec6/explore). However, this resource provides the file as a "Vector Tile Service" which is not editable. We needed an editable shapefile of the master boundary in order to clip all of our downstream data to the study area. Therefore, using the resource above, we traced exact boundary in ArcGIS Pro to create an editable shapefile. 

<embed type="text/html" src="figures/boundary_figures/pawnee_boundary_plot.html" width="800" height="800">

**Figure #:** This map shows the boundaries of the Pawnee National Grasslands. The master boundary shows the official extent of the Grasslands which includes a mix of federal, state, and privately owned property. The transparent areas are private property. The map shows the fragmented nature of land ownership on the grasslands. Notice the higher degre of contiguity of federally owned land on the western area of the grasslands.

### Subsetting to the Western Half of the Grasslands
In order to narrow our initial study area and potentially identify higher impact land swaps, we are focusing our study on the western half of the Grasslands. This area already has a higher degree of contiguity of federally owned land, and provides the potential to improve this further. 

<embed type="text/html" src="figures/boundary_figures/west_pawnee_boundary_plot.html" width="800" heigh="800">

**Figure #:** This map shows parcel data for the western Pawnee National Grasslands. Private property boundaries are included in white. 

The method for downloading and preparing the boundary data can be found in the 'boundaries.ipynb' in our [repository](https://github.com/maxwarnock/Pawnee-Grasslands-Project/tree/main/code). 


## Herbivores of Pawnee National Grasslands

The goal of this project is to identify land swap locations that will provide the highest ecological benefit. Therefore, we will incorporate species data into our analysis. Two foundational species on the Pawnee National Grasslands are Prairie dogs (*Cynomys ludovicianus*) and Pronghorn (*Antilocapra americana*). According to Kotliar et al, the Prairie Dog fits the criteria of a keystone species, providing important interactions between multiple parts of the grassland ecosystem. Pronghorn, while not usually referred to as a keystone species, are another important and iconic part of the grassland ecosystem (Millspaugh, et al). We use data from the [Global Biodiversity Information Facility (GBIF)](https://www.gbif.org/) to map the locations of these species to understand their presence and distribution on the grasslands.

<embed type="text/html" src="figures/gbif/gbif_animals_clipped_map.html" width="800" heigh="800">

**Figure #:** This map shows the distribution of Pronghorn and Prairie dog observations on the western Pawnee National Grasslands. GBIF data is collected by citizen scientists. 

### Considerations for GBIF Citizen Science Data
GBIF data is collected by citizen scientists through a variety of methods including popular tools like [iNaturalist](https://www.inaturalist.org/). Therefore, the distribution of species data can often influenced by factors such as accessability and population. For example, species observations are more likely to be recorded in areas where more people go outside. Inaccessible areas are often less recorded. This phenomenon can be observed in the above figure. For example, in the south eastern portion of the map, species observations are clustered along roads. This representation may be heavily influenced by human accessibility patterns, and not reflect the the actual distribution of the species.


# Works Cited

Kotliar, Natasha B., Brian J. Miller, Richard P. Reading, and Timothy W. Clark. "The Prairie Dog as a Keystone Species." In Conservation of the Black-Tailed Prairie Dog: Saving North America's Western Grasslands, edited by John Hoogland, [pp. 53–64]. Washington, DC: Island Press, 2006.

Millspaugh, Joshua, Jesse DeVoe, and Kelly Proffitt. Pronghorn Movement and Population Ecology Project: 2021 Annual Interim Report. Federal Aid in Wildlife Restoration Grant W-176-R. Missoula and Bozeman: Montana Fish, Wildlife & Parks and University of Montana, September 2021. https://fwp.mt.gov/binaries/content/assets/fwp/conservation/pronghorn/p-r-report---montana-pronghorn-project---2021.pdf.





