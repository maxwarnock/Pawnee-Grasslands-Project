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

- Parcel data: Weld County ArcGIS FeatureServer  
- Administrative boundaries: USFS  
- Species occurrences: GBIF  
- Derived datasets: Project-generated spatial layers  

---

## ⚙️ Workflow Overview
- 01_boundaries → defines study area + parcels (complete)
- 02/03_gbif → ecological value layers (complete)
- 04_land_value → economic metrics/values (complete)
- 05_connectivity_value → connection metrics/values (in progress)
- 06_contiguous_area → contiguous/edge ratio metrics/values (complete)
- 07_parcel_matrix → final integration (in progress)


---

## 📓 Notebooks Summary

### 01 – Boundaries  
Creates the **master and western Pawnee boundaries** and prepares parcel ownership layers for analysis.

**Key output:**
- `pawnee_master_west.shp`

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

### 06 – Contiguous Area  
Quantifies **total patch area** and **compactness**, identifying contiguous Federal ownership patches.

**Key contribution:**
- Identifies candidate parcels for increasing patch area and compactness.

---

### 07 – Parcel Matrix *(in progress)*  
Will integrate ecological, economic, connectivity and contiguous metrics into a unified decision framework.

---

## 📊 Outputs

- Cleaned parcel dataset with:
  - Ownership  
  - Ecological value
  - Connectivity value (in progress) 
  - Economic value  
  - Contiguity metrics  

- Spatial layers:
  - Master boundary  
  - Western Pawnee boundary  
  - Species occurrence maps  

---

## 🔁 Reproducibility

- Run notebooks in order (01 → 07)  
- All paths are relative to project root  
- Data sources (GBIF, parcel API) are dynamic and may change  

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
