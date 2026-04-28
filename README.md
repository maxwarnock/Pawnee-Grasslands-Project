# Pawnee National Grassland Land Swap Optimization

## 🌾 Overview

This project develops a geospatial framework to support **land swap optimization and fragmentation reduction** in the Pawnee National Grassland (Colorado). By integrating parcel ownership, ecological data, and spatial configuration metrics, the project identifies opportunities to consolidate federally managed lands and improve ecological function.

---

## 🎯 Project Goals

- Reduce landscape fragmentation through strategic land swaps  
- Increase contiguous federally managed land areas  
- Incorporate ecological and economic value into decision-making  
- Build a reproducible geospatial workflow for land optimization  

---

## 🗺️ Study Area

The analysis focuses on the **Pawnee National Grassland**, with spatial constraints defined using a custom boundary derived from USFS and parcel datasets.

---

## 📦 Data Sources

- Parcel data: Weld County ArcGIS FeatureServer  
- Administrative boundaries: USFS  
- Species occurrences: GBIF  
- Derived datasets: Project-generated spatial layers  

---

## ⚙️ Workflow Overview
- 01_boundaries → defines study area + parcels
- 02/03_gbif → ecological value layers
- 04_land_value → economic metrics/values
- 06_contiguous_area → contiguous/edge ratio metrics/values
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

### 05 – Connectivity / Contiguous Area  
Quantifies **parcel adjacency and fragmentation**, identifying contiguous ownership clusters.

**Key contribution:**
- Core metric for land consolidation potential

---

### 06 – Contiguous Area  
Quantifies **parcel adjacency and fragmentation**, identifying contiguous ownership clusters.

**Key contribution:**
- Core metric for land consolidation potential

---

### 06 – Parcel Matrix *(in progress)*  
Will integrate ecological, economic, and spatial metrics into a unified decision framework.

---

## 📊 Outputs

- Cleaned parcel dataset with:
  - Ownership  
  - Ecological value *(in progress)*  
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

## 👥 Contributors (CRediT Taxonomy)

## 👥 Contributor Roles (CRediT Taxonomy)

### 01 – Boundaries
| Role | Kayleigh Ward | Nate Hofford | Max Warnock |
|------|---------------|--------------|-------------|
| Conceptualization | ✓ |  | ✓ |
| Data Curation | ✓ |  | ✓ |
| Methodology | ✓ |  | ✓ |
| Software |  |  | ✓ |
| Validation | ✓ |  |  |
| Visualization | ✓ |  |  |
| Writing – Original Draft |  |  | ✓ |
| Writing – Review & Editing | ✓ |  |  |

---

### 02 – GBIF Animals
| Role | Kayleigh Ward | Nate Hofford | Max Warnock |
|------|---------------|--------------|-------------|
| Conceptualization | ✓ |  | ✓ |
| Data Curation | ✓ |  | ✓ |
| Methodology | ✓ |  | ✓ |
| Software |  |  | ✓ |
| Validation | ✓ |  |  |
| Visualization | ✓ |  |  |
| Writing – Review & Editing | ✓ |  |  |

---

### 03 – GBIF Grasses
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
| Conceptualization | ✓ | ✓ |  |
| Data Curation | ✓ | ✓ |  |
| Methodology | ✓ | ✓ |  |
| Software |  | ✓ |  |
| Validation | ✓ |  |  |
| Visualization | ✓ |  |  |
| Writing – Original Draft |  | ✓ |  |
| Writing – Review & Editing | ✓ |  |  |