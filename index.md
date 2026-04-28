---
layout: default
title: Pawnee National Grasslands Land Swap Project
---

### Final Project for GEOG 4563-5563: Earth Analytics Applications

### Our Team:
- Kayleigh Ward
- Nate Hofford
- Max Warnock

# Project Background:
This project centers around using geospatial and species data to optimize potential land swaps on the Pawnee National Grassland to consolidate ownership and de-fragment habitat. Our goal is create a public tool to identify these land swaps, and provide evidence for recommendations for state agencies. 



# Goals:
1. Create a tool that analyzes ownership patterns and measure fragmentation of federally owned land. [summer]
2. Identify high-impact parcels whose transfer would objectively maximize consolidation of federally owned land.
3. Synthesize recommendations for agencies to achieve various goals [summer]



# Data Overview:
<img src="images/data_overview.png" alt="data" width="800">  




# Pawnee National Grasslands Property Boundary Data   
This project relies on publically available property boundary data. The Pawnee National Grasslands are located in Weld County, and we used Weld County's GIS Hub to download parcel level vector data. This GeoDataFrame includes an attribute table with information about property ownership, address, and polygon geometry for each parcel. From this, we are able to select federal, state, and privately owned land and map these different property types.

### Grassland Master Boundary   
The Pawnee National Grasslands include a mix of federal, state, and privately owned land. After researching online, we were unable to find a shapefile for the master boundary (official extent) of the grasslands. A resource for the master boundary can be found here [Pawnee National Grasslands FSBaseMap](https://usfs.hub.arcgis.com/maps/9b7e938de9fc45aeaea4bfe4b8868ec6/explore). However, this resource provides the file as a "Vector Tile Service" which is not editable. We needed an editable shapefile of the master boundary in order to clip all of our downstream data to the study area. Therefore, using the resource above, we traced exact boundary in ArcGIS Pro to create an editable shapefile. 

<embed type="text/html" src="figures/boundary_figures/pawnee_boundary_plot.html" width="800" height="500">

**Figure #:** This map shows the boundaries of the Pawnee National Grasslands. The master boundary shows the official extent of the Grasslands which includes a mix of federal, state, and privately owned property. The transparent areas are private property. The map shows the fragmented nature of land ownership on the grasslands. Notice the higher degre of contiguity of federally owned land on the western area of the grasslands.

### Subsetting to the Western Half of the Grasslands   
In order to narrow our initial study area and potentially identify higher impact land swaps, we are focusing our study on the western half of the Grasslands. This area already has a higher degree of contiguity of federally owned land, and provides the potential to improve this further. 

<embed type="text/html" src="figures/boundary_figures/west_pawnee_boundary_plot.html" width="800" height="500">

**Figure #:** This map shows parcel data for the western Pawnee National Grasslands. Private property boundaries are included in white. 

The method for downloading and preparing the boundary data can be found in the 'boundaries.ipynb' in our [repository](https://github.com/maxwarnock/Pawnee-Grasslands-Project/tree/main/code). 


# Herbivores of Pawnee National Grasslands   

The goal of this project is to identify land swap locations that will provide the highest ecological benefit. Therefore, we will incorporate species data into our analysis. Two foundational species on the Pawnee National Grasslands are Prairie dogs (*Cynomys ludovicianus*) and Pronghorn (*Antilocapra americana*). According to Kotliar et al, the Prairie Dog fits the criteria of a keystone species, providing important interactions between multiple parts of the grassland ecosystem. Pronghorn, while not usually referred to as a keystone species, are another important and iconic part of the grassland ecosystem (Millspaugh, et al). We use data from the [Global Biodiversity Information Facility (GBIF)](https://www.gbif.org/) to map the locations of these species to understand their presence and distribution on the grasslands.

<embed type="text/html" src="figures/gbif/gbif_animals_clipped_map.html" width="800" height="500">

**Figure #:** This map shows the distribution of Pronghorn and Prairie dog observations on the western Pawnee National Grasslands. GBIF data is collected by citizen scientists. 

### Considerations for GBIF Citizen Science Data   
GBIF data is collected by citizen scientists through a variety of methods including popular tools like [iNaturalist](https://www.inaturalist.org/). Therefore, the distribution of species data can often influenced by factors such as accessability and population. For example, species observations are more likely to be recorded in areas where more people go outside. Inaccessible areas are often less recorded. This phenomenon can be observed in the above figure. For example, in the south eastern portion of the map, species observations are clustered along roads. This representation may be heavily influenced by human accessibility patterns, and not reflect the the actual distribution of the species.




# Grasses of Pawnee National Grassland




# Contiguous Area Measures
We built two evaluation criteria to measure contiguous area within Pawnee National Grassland. First, we defined contiguous patches for Federal parcels. These were defined as any two parcels that share at least one side. Touching corners did not count as contiguous.

<img src="figures/contiguous/contig_patch.png" alt="patch" width="800">  

***Figure n:*** (Left) Contiguous patches share at least one side. (Right) Parcels touching corners were not considered contiguous.

We then evaluated total area of eall contiguous patches to determine the largest Federal holdings. Optimizing for total area would allow managers to apply treatment to broader areas of land. 

<img src="figures/contiguous/contig_totarea.png" alt="totalarea" width="400">

***Figure n:*** Total area calculation.

Exterior edges of patches represent land that PNG cannot manage. To understand how compact each patch was, we calculated an interior edge ratio. This ratio is the sum of the interior edge lengths / sum of the exterior edge lengths. More compact patches will have a higher interior edge ratio. These compact patches minimize the interface between managed land and unmanaged land.

<img src="figures/contiguous/contig_edgerat.png" alt="edgeratio" width="800">

***Figure n:*** Edge ratio calculation.

We end up with two maps of federal patches colored by total area and internal edge ratio. Patches with high total area and high internal edge ratio would be candidates for recieving land swap. Low scores across these two metrics would be candidates for an outgoing swap.

<embed type="text/html" src="figures/contiguous/federal_patches_map.html" width="1000" height="575">

***Figure n:*** (Left) Total area patches, colored by area rank. Green patches have a higher total area compared to red patches. (Right) Interior edge patches, colored by score. Green patches have a higher ratio of interior edges.





