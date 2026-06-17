[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19864164.svg)](https://doi.org/10.5281/zenodo.19864164)

# Pawnee National Grassland Land Swap Optimization

## 🌾 Overview

This project develops a geospatial framework to support **land swap optimization and fragmentation reduction** in the Pawnee National Grassland (Colorado). By integrating parcel ownership, ecological data, and spatial configuration metrics, the project identifies opportunities to consolidate federally managed lands and improve ecological function.

This project is done in partnership with Grasslands Unlimited.

---

## 🎯 Project Goals

- Reduce landscape fragmentation through strategic land swaps in Western and Eastern Pawnee National Grasslands 
- Increase contiguous federally managed land areas  
- Incorporate ecological (biodiversity), connectivity (roads), and economic (land value) metrics into decision-making  
- Build a reproducible geospatial workflow for land optimization
- Build a public app to explore potential land swaps

---

## 🗺️ Study Area

The analysis focuses on the **Pawnee National Grassland**, with spatial constraints defined using a custom boundary derived from USFS and parcel datasets. The Pawnee National Grassland is located in Weld County, Colorado, USA. 

---

## 📦 Data Sources

- **Pawnee National Grasslands Boundary:** [U.S. Forestry Service, Administrative Boundaries (shapefiles/polygons)](https://data.fs.usda.gov/geodata/edw/datasets.php)  
  Provides boundary area of the Pawnee Grassland Preserve to clip all rasters to. Due to issues with no publicly available shapefile of the full grassland extent, Max Warnock carefully created our own original boundary shapefile to use for this project.

  
- **Parcel data:** [Weld County ArcGIS FeatureServer](https://gishub.weldgov.com/datasets/37d03225dab04760b4fd9f5f531d313e_0/explore?location=40.501097%2C-104.312267%2C9)  
  This data is provided by Weld County and was already in a usable format, and was also compatible with an API call. We use the Weld County GIS portal as it is updated regularly, and provided the following information to our team and analysis:  
    - i. Provides surface area to calculate which parcels are more efficient to swap.   
    - ii. Provides landowner data (federal, state, private) such that we swap parcels either between federal and state owners or state and private owners.   
    - iii. Provides tax assessed value and total land values such that we swap parcels of similar value.   


- **Species occurrences:** [Global Biodiversity Information Facility](https://www.gbif.org/)  
  GBIF data on foundational/keystone species in grassland stands (observations/points)  
  Provide species observation data (points) of 2-3 foundational species. Including prairie dogs and antelope and 5 grass species as identified by the USDA PLANTS database. (https://plants.sc.egov.usda.gov/) 


- **Oil and Gas Data:** [Colorado Energy and Carbon Management Commission GIS page](https://ecmc.colorado.gov/data-maps-reports/downloadable-data-documents)  
Colorado Energy & Carbon Management Commission—Daily Activity Dashboard [https://ecmc.colorado.gov/data-dashboard] (shapefiles/polygons and observations/points)  
As our partner does not want to swap land with important oil and gas infrastructure we use a variety of oil and gas datasets from Colorado’s ECMC, including:  
Main data page which includes code guides and instructions on how to download ECMC data: https://ecmc.colorado.gov/data-maps-reports/downloadable-data-documents   
    - i. Active and Plugged Wells: https://ecmc.state.co.us/documents/data/downloads/gis/WELLS_SHP.ZIP   
    - ii. Active Well Permits: https://ecmc.state.co.us/documents/data/downloads/gis/PERMITS_SHP.ZIP  
    - iii. Pending Well Permits: https://ecmc.state.co.us/documents/data/downloads/gis/PERMITS_PENDING_SHP.ZIP   
    - iv. Oil and Gas Field Polygons: https://ecmc.state.co.us/documents/data/downloads/gis/COGCC_FIELDS_SHP.zip


- **Prairie Dog Data:** 2012 prairie dog data provided directly by Grasslands Unlimited to better refine the GBIF observational data.
 
  
- **Roads and Connectivity Data:** [TIGER/Line Shapefile, 2019, state, Colorado, Primary and Secondary Roads State-based Shapefile](https://catalog.data.gov/dataset/tiger-line-shapefile-2019-state-colorado-primary-and-secondary-roads-state-based-shapefile)


- **Water:** [State of Colorado, Division of Water Resources](https://dwr.colorado.gov/services/data-information/gis)
Due to differences in the value of a parcel with water access to those that do not, we use the following GIS layers with the parcels: surface water and groundwater. This way we have an ecological “water” value to also add to the parcels (e.g., 0=no water, 1=water presence)




- **Derived datasets:** Project-generated spatial layers 


---

## ⚙️ Workflow Overview
- 01_boundaries → defines study area + parcels (complete)
- 02/03_gbif → ecological value layers (complete)
- 04_land_value → economic metrics/values (complete)
- 05_connectivity_value → connection metrics/values (in progress)
- 06_oil_gas → oil and gas locations (in progress)
- 07_contiguous_area → contiguous/edge ratio metrics/values (complete)
- 08_parcel_matrix → swap identification (in progress)


---

## 📓 Notebooks Summary

### 01 – Boundaries  
Creates the **master and western Pawnee boundaries** and prepares parcel ownership layers for analysis.

**Key output:**
- `master_bound_gdf`

---

### 02 – GBIF Animals  
Processes prairie dog and pronghorn observations to generate **parcel-level ecological indicators**.

**Key contribution:**
- Links biodiversity data to parcel units

---

### 03 – GBIF Grasses  
Maps five native grass species and produces **interactive spatial outputs** of species distributions.

**Key contribution:**
- Establishes vegetation-based ecological context and links biodiversity data to parcel units

---

### 04 – Land Value  
Calculates **parcel-level economic metrics** (market and assessed value per acre).

**Key contribution:**
- Normalizes value across parcels for comparison

---

### 05 – Connectivity *(in progress)*  
Quantifies **parcel touching roads based on buffer**, to identify easy to manage parcels.

**Key contribution:**
- Normalizes connection values across parcels for comparison

---

### 06 - Oil and Gas *(in progress)*
Downloads oil and gas data and maps locations of active and pending infrastructure. 

**Key contribution:**
Output map of the active and pending wells and oil fields within the grasslands: `wells_filtered_fed_state_status.html`

---

### 07 – Contiguous Area  
Quantifies **total patch area** and **compactness**, identifying contiguous Federal ownership patches.

**Key contribution:**
- Identifies candidate parcels for increasing patch area and compactness.

---

### 08 – Parcel Matrix *(in progress)*  
Will integrate ecological, economic, connectivity and contiguous metrics into a unified decision framework. 

---

## 📊 Outputs

- Cleaned parcel dataset with:
  - Ownership  
  - Ecological value
  - Connectivity value (in progress) 
  - Economic value
  - Oil and gas locations
  - Contiguity (interior edge ratio) metrics  

---

## 🔁 Reproducibility

**1.** This project uses a conda environment. We recommend using VSCode. To create and activate the environment, open the repository in VSCode and run these commands:

`conda env create -f environment.yml`   
`conda activate pawnee-grasslands`

Then launch the project Jupyter notebooks.


Requirements: conda (or Anaconda) must be installed. Packages are pulled from conda-forge and defaults channels.

**2.**  
- Run notebooks in order (01 → 08)  
- Notebooks 02 and 03 require you to login to a GBIF account. Create one at [GBIF.org](gbif.org)
- Notebooks 02 and 03 require GBIF downloads which can take anywhere from 15 minutes to 3 hours
- All necessary data is downloaded from API calls 
- All paths are relative to project root  
- Data sources (GBIF, parcel API, oil and gas data) are dynamic and may change  

---


## Works Cited

Baynard, C. W., Mjachina, K., Richardson, R. D., Schupp, R. W., Lambert, J. D., & Chibilyev, A. A. (2017). Energy development in Colorado’s Pawnee National Grasslands: Mapping and measuring the disturbance footprint of renewables and non-renewables. Environmental Management, 59, 995–1016. https://doi.org/10.1007/s00267-017-0846-z

Hazlett, Donald L. 1998. Vascular plant species of the Pawnee National Grassland. General Technical Report RMRS-GTR-17. Fort Collins, CO: U.S. Department of Agriculture, Forest Service, Rocky Mountain Research Station. 26 p. https://research.fs.usda.gov/download/treesearch/25015.pdf

Kotliar, Natasha B., Brian J. Miller, Richard P. Reading, and Timothy W. Clark. “The Prairie Dog as a Keystone Species.” In Conservation of the Black-Tailed Prairie Dog: Saving North America’s Western Grasslands, edited by John Hoogland, pp. 53–64. Washington, DC: Island Press, 2006.

Millspaugh, Joshua, Jesse DeVoe, and Kelly Proffitt. Pronghorn Movement and Population Ecology Project: 2021 Annual Interim Report. Federal Aid in Wildlife Restoration Grant W-176-R. Missoula and Bozeman: Montana Fish, Wildlife & Parks and University of Montana, September 2021. https://fwp.mt.gov/binaries/content/assets/fwp/conservation/pronghorn/p-r-report—montana-pronghorn-project—2021.pdf.

Powers, L. C., Larsen, A. E., Leonard, B., & Plantinga, A. J. (2022). Reconnecting stranded public lands is a win-win for conservation and people. Biological Conservation, 270, 109557. https://doi.org/10.1016/j.biocon.2022.109557

Rhoads, Dorothy, and Lee Rhoads. (n.d.). History of the Pawnee National Grassland. U.S. Forest Service. https://www.fs.usda.gov/media/71487

Riitters, K. H. (2013). Fragmentation of forest, grassland, and shrubland. In K. M. Potter & B. L. Conkling (Eds.), Forest Health Monitoring: National status, trends, and analysis 2010 (Gen. Tech. Rep. SRS-GTR-176, pp. 53–65). U.S. Department of Agriculture, Forest Service, Southern Research Station.

U.S. Forest Service. (n.d.). The national grasslands story. U.S. Department of Agriculture. https://www.fs.usda.gov/managing-land/national-forests-grasslands/national-grasslands/about-us

Weld County GIS. (2026). Weld County real property parcels [Dataset]. Weld County GIS Hub. https://gishub.weldgov.com/datasets/37d03225dab04760b4fd9f5f531d313e_0/explore


---

## 👥 Contributor Roles (CRediT Taxonomy)

### 01 – Boundaries
| Role | Kayleigh Ward | Nate Hofford | Max Warnock |
|------|---------------|--------------|-------------|
| Conceptualization | ✓ |  | ✓ |
| Data Curation | ✓ |  | ✓ |
| Methodology | ✓ |  | ✓ |
| Software |  |  | ✓ |
| Validation | ✓ |  |  |
| Visualization |  |  | ✓ |
| Writing – Original Draft |  |  | ✓ |
| Writing – Review & Editing | ✓ |  |  |

---

### 02 – GBIF Animals
| Role | Kayleigh Ward | Nate Hofford | Max Warnock |
|------|---------------|--------------|-------------|
| Conceptualization | ✓ |  | ✓ |
| Data Curation |  |  | ✓ |
| Methodology | ✓ |  | ✓ |
| Software |  |  | ✓ |
| Validation | ✓ |  |  |
| Visualization |  |  | ✓ |
| Writing – Original Draft |  |  | ✓ |
| Writing – Review & Editing | ✓ |  |  |

---

### 03 – GBIF Grasses
| Role | Kayleigh Ward | Nate Hofford | Max Warnock |
|------|---------------|--------------|-------------|
| Conceptualization | ✓ |  | ✓ |
| Data Curation | ✓ |  |  |
| Methodology | ✓ |  | ✓ |
| Software | ✓ |  |  |
| Visualization | ✓ |  |  |
| Writing – Original Draft | ✓ |  |  |
| Writing – Review & Editing | ✓ |  |  |

---

### 04 – Land Value
| Role | Kayleigh Ward | Nate Hofford | Max Warnock |
|------|---------------|--------------|-------------|
| Conceptualization | ✓ |  |  |
| Data Curation | ✓ |  |  |
| Methodology | ✓ |  |  |
| Software | ✓ |  |  |
| Visualization | ✓ |  |  |
| Writing – Original Draft | ✓ |  |  |
| Writing – Review & Editing | ✓ |  |  |

---

### 06 – Contiguous Area
| Role | Kayleigh Ward | Nate Hofford | Max Warnock |
|------|---------------|--------------|-------------|
| Conceptualization | ✓ | ✓ | ✓ |
| Data Curation | ✓ | ✓ | ✓ |
| Methodology | ✓ | ✓ | ✓ |
| Software |  | ✓ |  |
| Validation |  | ✓ |  |
| Visualization |  | ✓ |  |
| Writing – Original Draft |  | ✓ |  |
| Writing – Review & Editing | ✓ |  |  |
