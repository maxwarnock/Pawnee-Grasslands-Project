[![DOI](https://zenodo.org/badge/1203065969.svg)](https://doi.org/10.5281/zenodo.19864164)

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
