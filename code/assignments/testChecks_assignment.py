# Tests & Checks assignment
## Group members: Max Warnock, Kayleigh Ward, Nate Hofford

## Load in necessary libraries for both examples and set working path to root
### file paths, OS operations, utilities
import os
import json
import pathlib
import zipfile
import time
from glob import glob
from getpass import getpass

### data handling 
import pandas as pd
import geopandas as gpd

### web requests / data download
import requests
import gdown

### geospatial visualization 
import holoviews as hv
import hvplot.pandas
import cartopy.crs as ccrs

### GBIF API access
import pygbif.occurrences as occ
import pygbif.species as species


########################### Example 1 - Parcel Download source ###########################
## Previosly, we were replying on a downloaded parcel dataset that Max was storing on his Google Drive.
## While this is stable and something we can control, it is better to download straight from the Weld Co.
## GIS database. We added a fix that downloads from Weld Co. first, and uses the Google Drive link
## as a fallback. The means we can update the tool with new Weld Co. data easily, but ensures
## we have a stable data source in case the Weld Co. data changes.

## It also means that if Max's google drive changes we have an alternate version from Weld Co. Updating
## this function means we have a check that ensure a stable parcel dataset that all the downstream
## processing relies on.

########################### OLD CODE ###########################
## This code loaded in the necessary paths for directories used specifically for this notebook

### Google Drive url
county_parcel_url = "https://drive.google.com/uc?export=download&id=1B1xTWb-Dfy9vJBFPB3hiSRex3j6eZ__2"

### local zip path
zip_path = os.path.join(county_parcel_dir, "county_parcels.zip")

### download
gdown.download(county_parcel_url, zip_path, quiet=False)

print("Downloaded:", zip_path)

### unzip
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall(county_parcel_dir)

print("Extracted to:", county_parcel_dir)

########################### NEW CODE ###########################
## This new code allows the user to select which data download they want to use. Defaults to Weld Co.
## but falls back on Max's google drive if that fails. This also has a check to ensure the columns are 
## consistent between the two versions of the parcel dataset.

# ============================================================
# PARCEL DATA SOURCE SELECTION
#
# Set parcel_source to choose how county parcel data is downloaded.
#
#   "weld_gis"     — Query from Weld Co. ArcGIS FeatureServer (default).
#                    Falls back to "google_drive" automatically if the 
#                    server is unreachable.
#
#   "google_drive" — Static backup on Google Drive (Max's copy).
#                    Included just in case the Weld Co. data goes down.
#
# Parcel URLs:
WELD_GIS_URL     = "https://services.arcgis.com/ewjSqmSyHJnkfBLL/arcgis/rest/services/Parcels_open_data/FeatureServer/0/query"
GOOGLE_DRIVE_URL = "https://drive.google.com/uc?export=download&id=1B1xTWb-Dfy9vJBFPB3hiSRex3j6eZ__2"
# ============================================================

parcel_source = "weld_gis"   # change this to google_drive if you want to use that version

print(f"Parcel source set to: '{parcel_source}'")

## Code from Kayleigh's notebook 04_land_value.ipynb transferred to here for handling
## ESRI download from Weld Co.
def polygon_to_esri_json(geom):
    """Convert a shapely Polygon/MultiPolygon to Esri JSON rings for use in ArcGIS queries."""
    polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    rings = []
    for poly in polys:
        rings.append([[float(x), float(y)] for x, y in poly.exterior.coords])
        for interior in poly.interiors:
            rings.append([[float(x), float(y)] for x, y in interior.coords])
    return {"rings": rings, "spatialReference": {"wkid": 4326}}

## Pulls parcel data with a small buffer on the master boundary 
## to make sure we don't miss anything.
def query_parcels_by_boundary(boundary_gdf, buffer_deg=0.0, out_fields="*", batch_size=1000, max_pages=100):
    """
    Query the Weld Co. ArcGIS FeatureServer for all parcels that intersect
    the given boundary GeoDataFrame. Requests all available fields (out_fields='*').

    Parameters
    ----------
    boundary_gdf : GeoDataFrame
        The boundary to use as a spatial filter (e.g. pawnee_master_boundary_gdf).
        Must be in EPSG:4326.
    buffer_deg : float
        Buffer in decimal degrees set to 0.01 (~ 1 km). Get parcels just outside the Pawnee grassland.
    """
    frames = []
    offset = 0
    out_str = ",".join(out_fields) if isinstance(out_fields, list) else out_fields

    ### Dissolve boundary to a single geometry and buffer
    query_geom = boundary_gdf.to_crs(epsg=4326).geometry.union_all()
    if buffer_deg > 0:
        query_geom = query_geom.buffer(buffer_deg)
    esri_json = polygon_to_esri_json(query_geom)

    for page in range(max_pages):
        params = {
            "where": "1=1",
            "geometry": json.dumps(esri_json),
            "geometryType": "esriGeometryPolygon",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": out_str,
            "returnGeometry": "true",
            "outSR": 4326,
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": batch_size,
        }
        r = requests.post(WELD_GIS_URL, data=params, timeout=120)

        if not r.ok:
            print("HTTP status:", r.status_code)
            print("Response preview:", r.text[:300])
            r.raise_for_status()

        data = r.json()

        if "error" in data:
            raise RuntimeError(f"ArcGIS error: {data['error']}")

        features = data.get("features", [])
        if not features:
            break

        batch_gdf = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")
        frames.append(batch_gdf)
        total = sum(len(f) for f in frames)
        print(f"Page {page + 1}: fetched {len(features):,} parcels (total: {total:,})")

        if len(features) < batch_size:
            break

        offset += batch_size

    if not frames:
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
    return gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")

## Add in lat/long columns to downloaded data + crs to WGS84
def harmonize_parcel_schema(gdf):
    """
    Normalize a parcel GeoDataFrame for consistent downstream use:
    - Reproject to EPSG:4326 (Google Drive .shp is in Web Mercator)
    - Ensure latitude/longitude attribute columns are present
      (derived from geometry centroids if absent from the source)
    All columns from the source are kept as-is — no filtering applied.
    """
    gdf = gdf.copy()

    ### Reproject to EPSG:4326
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    ### Add latitude/longitude from geometry centroids if not present
    if "latitude" not in gdf.columns:
        centroids = gdf.geometry.centroid
        gdf["latitude"]  = centroids.y
        gdf["longitude"] = centroids.x

    return gdf


### Load from Google Drive backup
def _load_from_google_drive():
    zip_path = os.path.join(county_parcel_dir, "county_parcels.zip")
    gdown.download(GOOGLE_DRIVE_URL, zip_path, quiet=False)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(county_parcel_dir)
    shp_path = os.path.join(county_parcel_dir, "Parcels_open_data.shp")
    return gpd.read_file(shp_path)


### Download
county_parcel_gdf = None
source_used = None

if parcel_source == "weld_gis":
    try:
        ### Pull parcels that only intersect the master boundary + buffer.
        county_parcel_gdf = query_parcels_by_boundary(
            pawnee_master_boundary_gdf,
            buffer_deg=0.01
        )
        source_used = "Weld Co. ArcGIS FeatureServer (Pawnee boundary)"
        print(f"Downloaded {len(county_parcel_gdf):,} parcels from {source_used}")
    except Exception as e:
        print(f"WARNING: Weld Co. ArcGIS download failed: {e}")
        print("Falling back to Google Drive backup...")
        county_parcel_gdf = _load_from_google_drive()
        source_used = "Google Drive backup (auto-fallback)"
        print(f"Loaded {len(county_parcel_gdf):,} parcels from {source_used}")

elif parcel_source == "google_drive":
    county_parcel_gdf = _load_from_google_drive()
    source_used = "Google Drive"
    print(f"Loaded {len(county_parcel_gdf):,} parcels from {source_used}")

else:
    raise ValueError(f"Unknown parcel_source: '{parcel_source}'. Use 'weld_gis' or 'google_drive'.")

### Apply lat/long + reprojection
county_parcel_gdf = harmonize_parcel_schema(county_parcel_gdf)
print(f"Schema standardized — {len(county_parcel_gdf):,} parcels, {len(county_parcel_gdf.columns)} columns")

### Save the raw parcel data as a .gpkg
raw_parcel_path = os.path.join(county_parcel_dir, "county_parcels_raw.gpkg")
county_parcel_gdf.to_file(raw_parcel_path, driver="GPKG")
print(f"Saved raw parcel data ({source_used}) to: {raw_parcel_path}")

### Check it
county_parcel_gdf.head()


########################### Example 2 - Final script checks ###########################
## Script 08_build_parcel_swap_site.py is the code that pulls all the maps for our assigment for 
## the final app. We have a couple places built into this where checks are in place.

# Check to ensure the proposals data product is present
## This if statement raises and error if the 07_parcel_matrix.ipynb hasn't been run yet.
## The app is entirely reliant on the parcel_matrix, so this check is essential for updating the app.
def load_ranked_proposals_from_notebook(root: Path) -> tuple[pd.DataFrame, int | None]:
    notebook_path = root / "code" / "07_parcel_matrix.ipynb"
    notebook = nbformat.read(notebook_path, as_version=4)

    output_text = ""
    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            if output.get("output_type") != "stream":
                continue
            text = "".join(output.get("text", ""))
            if "LAND SWAP PROPOSAL SUMMARY" in text:
                output_text = text
                break
        if output_text:
            break

    if not output_text:
        raise ValueError("Could not find ranked proposal output in code/07_parcel_matrix.ipynb.")

# Check to make sure parcel centroids geometry is valid
## Our tool has a feature that visualizes the swaps by connecting them with a line.
## It also uses the centroid to control which parcels are too far away from each other to swap.
## This check ensure that the parcel centroid geometry is a point, so both of these features
## will work correctly.
parcel_centroids = parcels_4326.geometry.representative_point()
centroid_lookup: dict[str, list[float]] = {}
for parcel_id, point in zip(parcels_4326["PARCEL"], parcel_centroids, strict=False):
    if not isinstance(point, Point):
        raise TypeError(f"Representative point for parcel {parcel_id} is not a Point.")
    centroid_lookup[str(parcel_id)] = [round(float(point.y), 6), round(float(point.x), 6)]