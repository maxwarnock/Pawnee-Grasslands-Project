# Modularization assignment
## Group members: Max Warnock, Kayleigh Ward, Nate Hofford

## Load in necessary libraries for both examples and set working path to root
# Libraries for path/files
import os
import json
import math
import pathlib 

# Pulling data and plotting geospatial land values
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape

pd.set_option("display.max_columns", 100)
pd.set_option("display.width", 200)

# Set up root file path
# Walk up from the current directory to find the repo root (contains .git)
_cwd = pathlib.Path(os.getcwd()).resolve()
repo_root = next(
    (p for p in [_cwd] + list(_cwd.parents) if (p / '.git').exists()),
    _cwd
)
os.chdir(repo_root)

data_dir = os.path.join(repo_root, 'data')
os.makedirs(data_dir, exist_ok=True)

print(f'Repo root: {repo_root}')

########################### Example 1 - Improving reproducability ###########################
## This modification deals with the 04_land_value.ipynb notebook

########################### OLD CODE ###########################
## This code loaded in the necessary paths for directories used specifically for this notebook

# Secondary directories for land values
data_dir = repo_root / "data"
boundary_dir = data_dir / "boundaries"
processed_dir = data_dir / "processed"
parcel_dir = processed_dir / "land_values"
fig_dir = repo_root / "figures" / "land_values"

for folder in [data_dir, boundary_dir, processed_dir, parcel_dir, fig_dir]:
    folder.mkdir(parents=True, exist_ok=True)

print(f"Repo root: {repo_root}")
print(f"Parcel output dir: {parcel_dir}")

# Use shapefile made in 'boundaries' notebook
###---BUG NOTE---###
# MAKE SURE to set `pawnee_boundary_path` to YOUR LOCAL path of the shapefile.
# Otherwise this code this not work. The path will have been generated from `01_boundaries`
pawnee_boundary_path = r"C:\Users\kayle\Desktop\earth-analytics\Pawnee-Grasslands-Project\data\boundaries\boundary-data-final-west\master_boundary\pawnee_master_west.shp"

pawnee = gpd.read_file(pawnee_boundary_path)
pawnee = pawnee[pawnee.geometry.notna()].copy()

print("Loaded:", pawnee_boundary_path)
print("Original CRS:", pawnee.crs)
display(pawnee.head())

# Reproject to EPSG:4326 only if needed
if pawnee.crs != "EPSG:4326":
    pawnee_4326 = pawnee.to_crs(epsg=4326)
else:
    pawnee_4326 = pawnee.copy()

# Dissolve to one geometry for querying/clipping
pawnee_union_geom = pawnee_4326.geometry.union_all()

pawnee_union = gpd.GeoDataFrame(
    {"geometry": [pawnee_union_geom]},
    crs="EPSG:4326"
)

print("Query/overlay CRS:", pawnee_union.crs)
print("Geometry type:", pawnee_union.geom_type.iloc[0])

########################### NEW CODE ###########################
## This new code removed the hard-coded file pathway so that any user that has run 01_boundaries 
## can use this code without having to change the path.

# Secondary directories for land values
data_dir = repo_root / "data"
# Path to the boundary outline
boundary_dir = data_dir / "boundaries" 
# Path to master boundary file (overall outline)
master_boundary_dir = boundary_dir / "boundary-data-final" / "master_boundary"
processed_dir = data_dir / "processed"
parcel_dir = processed_dir / "land_values"
fig_dir = repo_root / "figures" / "land_values"

for folder in [data_dir, boundary_dir, processed_dir, parcel_dir, fig_dir]:
    folder.mkdir(parents=True, exist_ok=True)

print(f"Repo root: {repo_root}")
print(f"Parcel output dir: {parcel_dir}")

# Use shapefile made in 'boundaries' notebook
pawnee_master_boundary = master_boundary_dir / "pawnee_master.shp"

pawnee = gpd.read_file(pawnee_master_boundary)
pawnee = pawnee[pawnee.geometry.notna()].copy()

print("Loaded:", pawnee_master_boundary)
print("Original CRS:", pawnee.crs)
display(pawnee.head())

# Reproject to EPSG:4326 only if needed
if pawnee.crs != "EPSG:4326":
    pawnee_4326 = pawnee.to_crs(epsg=4326)
else:
    pawnee_4326 = pawnee.copy()

# Dissolve to one geometry for querying/clipping
pawnee_union_geom = pawnee_4326.geometry.union_all()

pawnee_union = gpd.GeoDataFrame(
    {"geometry": [pawnee_union_geom]},
    crs="EPSG:4326"
)

print("Query/overlay CRS:", pawnee_union.crs)
print("Geometry type:", pawnee_union.geom_type.iloc[0])



########################### Example 2 - Modularize plotting ###########################
## Each plot was generated separately in a different cell of the notebook.
## While this really isn't a major issue, I though streamlining them using functions
## would allow for the user to modify / add plots more easily without having
## to scroll around through multiple cells.
## Note: these are two separate plotting functions that are now each modular.

########################### OLD CODE ###########################
# Mapping helper function
# These functions keep map formatting and saving consistent across figures
# This is also helpful for faster map creation later if there is any other land value that gets mapped

map_output_dir = fig_dir
map_output_dir.mkdir(parents=True, exist_ok=True)


def format_land_value_map(ax, title):
    """Apply common title and longitude/latitude axis labels to parcel maps."""
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.ticklabel_format(style="plain", useOffset=False)
    return ax


def save_land_value_map(fig, filename):
    """Save a map to the land_values figure folder."""
    output_path = map_output_dir / filename
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved map: {output_path}")
    return output_path

# Simple TOTALACT map
# Do not constrain vmax yet
fig, ax = plt.subplots(figsize=(8, 8))
pawnee_union.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.8)
parcels.plot(ax=ax, column="TOTALACT", legend=True, linewidth=0.2)
format_land_value_map(ax, "Pawnee parcels by TOTALACT")
save_land_value_map(fig, "pawnee_parcels_totalact.png")
plt.show()

# Simple LANDASD map
# Do not constrain vmax yet
fig, ax = plt.subplots(figsize=(8, 8))
pawnee_union.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.8)
parcels.plot(ax=ax, column="LANDASD", legend=True, linewidth=0.2)
format_land_value_map(ax, "Pawnee parcels by LANDASD")
save_land_value_map(fig, "pawnee_parcels_landasd.png")
plt.show()

# Federal mapping per acre (LANDASD)
# As size affects value greatly, the mapping here tries to contain extreme values.
# Here we calculate LANDASD per acre instead of per parcel.

usa = parcels[parcels["NAME"] == "U S A"].copy()
usa["landasd_per_acre"] = usa["LANDASD"] / usa["GIS_Acres"]

fig, ax = plt.subplots(figsize=(8, 8))

# Constrain vmax for better comparison
vmin = 0
vmax = 500

pawnee_union.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.8)
usa.plot(
    column="landasd_per_acre",
    cmap="viridis",
    legend=True,
    ax=ax,
    vmin=vmin,
    vmax=vmax,
    linewidth=0.2
)

format_land_value_map(ax, "Federal LANDASD per acre")
save_land_value_map(fig, "federal_landasd_per_acre.png")
plt.show()

# Colorado mapping per acre (LANDASD)
# As size affects value greatly, the mapping here tries to contain extreme values.
# Here we calculate LANDASD per acre instead of per parcel.

co = parcels[parcels["NAME"] == "COLORADO STATE OF"].copy()
co["landasd_per_acre"] = co["LANDASD"] / co["GIS_Acres"]

fig, ax = plt.subplots(figsize=(8, 8))

# Constrain vmax for better comparison
vmin = 0
vmax = 500

pawnee_union.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.8)
co.plot(
    column="landasd_per_acre",
    cmap="viridis",
    legend=True,
    ax=ax,
    vmin=vmin,
    vmax=vmax,
    linewidth=0.2
)

format_land_value_map(ax, "Colorado LANDASD per acre")
save_land_value_map(fig, "colorado_landasd_per_acre.png")
plt.show()

# Federal mapping per acre (TOTALACT)
usa_act = parcels[parcels["NAME"] == "U S A"].copy()
usa_act["totalact_per_acre"] = usa_act["TOTALACT"] / usa_act["GIS_Acres"]

fig, ax = plt.subplots(figsize=(8, 8))

# Constrain vmax
vmin = 0
vmax = 1000

pawnee_union.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.8)
usa_act.plot(
    column="totalact_per_acre",
    cmap="viridis",
    legend=True,
    ax=ax,
    vmin=vmin,
    vmax=vmax,
    linewidth=0.2
)

format_land_value_map(ax, "Federal TOTALACT per acre")
save_land_value_map(fig, "federal_totalact_per_acre.png")
plt.show()

# Colorado mapping per acre (TOTALACT)
co_act = parcels[parcels["NAME"] == "COLORADO STATE OF"].copy()
co_act["totalact_per_acre"] = co_act["TOTALACT"] / co_act["GIS_Acres"]

fig, ax = plt.subplots(figsize=(8, 8))

# Constrain vmax
vmin = 0
vmax = 1000

pawnee_union.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.8)
co_act.plot(
    column="totalact_per_acre",
    cmap="viridis",
    legend=True,
    ax=ax,
    vmin=vmin,
    vmax=vmax,
    linewidth=0.2
)

format_land_value_map(ax, "Colorado TOTALACT per acre")
save_land_value_map(fig, "colorado_totalact_per_acre.png")
plt.show()


########################### NEW CODE ###########################
## This new code applies similar logic to the raw land values 
## function(not normalized) by acreage to all the plotting. 
## It reduces the four mapping calls at the end to just a function 
## and a list of plots to call.

# Mapping helper functions
# Keep map formatting, saving, and choropleth creation consistent across figures.

map_output_dir = fig_dir
map_output_dir.mkdir(parents=True, exist_ok=True)


def format_land_value_map(ax, title):
    """Apply common title and longitude/latitude axis labels to parcel maps."""
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.ticklabel_format(style="plain", useOffset=False)
    return ax


def save_land_value_map(fig, filename):
    """Save a map to the land_values figure folder."""
    output_path = map_output_dir / filename
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved map: {output_path}")
    return output_path


def plot_parcel_value_map(
    data_gdf,
    boundary_gdf,
    column,
    title,
    filename,
    vmin=None,
    vmax=None,
    cmap="viridis",
    figsize=(8.0, 8.0),
):
    """Plot a parcel choropleth with a boundary overlay and save the figure."""
    fig, ax = plt.subplots(figsize=figsize)
    boundary_gdf.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=0.8)

    plot_kwargs = {
        "column": column,
        "cmap": cmap,
        "legend": True,
        "ax": ax,
        "linewidth": 0.2,
    }
    if vmin is not None and vmax is not None:
        plot_kwargs["vmin"] = vmin
        plot_kwargs["vmax"] = vmax
        plot_kwargs["norm"] = mcolors.Normalize(vmin=vmin, vmax=vmax)

    data_gdf.plot(**plot_kwargs)
    format_land_value_map(ax, title)
    save_land_value_map(fig, filename)
    plt.show()


def plot_owner_value_per_acre(
    parcels_gdf,
    boundary_gdf,
    owner_name,
    value_col,
    per_acre_col,
    title,
    filename,
    vmax=500.0,
    vmin=0.0,
    cmap="viridis",
    figsize=(8.0, 8.0),
):
    """Filter parcels by owner, compute per-acre value, and plot a choropleth map."""
    subset = parcels_gdf[parcels_gdf["NAME"] == owner_name].copy()
    subset[per_acre_col] = subset[value_col] / subset["GIS_Acres"]

    plot_parcel_value_map(
        data_gdf=subset,
        boundary_gdf=boundary_gdf,
        column=per_acre_col,
        title=title,
        filename=filename,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        figsize=figsize,
    )

# Full-parcel value maps (no per-acre normalization)
PARCEL_VALUE_PLOTS = [
    {
        "column": "TOTALACT",
        "title": "Pawnee parcels by TOTALACT",
        "filename": "pawnee_parcels_totalact.png",
    },
    {
        "column": "LANDASD",
        "title": "Pawnee parcels by LANDASD",
        "filename": "pawnee_parcels_landasd.png",
    },
]

for cfg in PARCEL_VALUE_PLOTS:
    plot_parcel_value_map(
        data_gdf=parcels,
        boundary_gdf=pawnee_union,
        column=cfg["column"],
        title=cfg["title"],
        filename=cfg["filename"],
    )

# Per-owner value-per-acre maps
OWNER_VALUE_PLOTS = [
    {
        "owner_name": "U S A",
        "value_col": "LANDASD",
        "per_acre_col": "landasd_per_acre",
        "title": "Federal LANDASD per acre",
        "filename": "federal_landasd_per_acre.png",
        "vmax": 500.0,
    },
    {
        "owner_name": "COLORADO STATE OF",
        "value_col": "LANDASD",
        "per_acre_col": "landasd_per_acre",
        "title": "Colorado LANDASD per acre",
        "filename": "colorado_landasd_per_acre.png",
        "vmax": 500.0,
    },
    {
        "owner_name": "U S A",
        "value_col": "TOTALACT",
        "per_acre_col": "totalact_per_acre",
        "title": "Federal TOTALACT per acre",
        "filename": "federal_totalact_per_acre.png",
        "vmax": 1000.0,
    },
    {
        "owner_name": "COLORADO STATE OF",
        "value_col": "TOTALACT",
        "per_acre_col": "totalact_per_acre",
        "title": "Colorado TOTALACT per acre",
        "filename": "colorado_totalact_per_acre.png",
        "vmax": 1000.0,
    },
]

for cfg in OWNER_VALUE_PLOTS:
    plot_owner_value_per_acre(
        parcels_gdf=parcels,
        boundary_gdf=pawnee_union,
        owner_name=cfg["owner_name"],
        value_col=cfg["value_col"],
        per_acre_col=cfg["per_acre_col"],
        title=cfg["title"],
        filename=cfg["filename"],
        vmax=cfg["vmax"],
    )


# Reflection
### Which parts of the code did I choose to modularize / improve reproducability?
#### As we come up on the end of the project, I am going through and re-running the
#### notebooks to make sure they all work reproducibly. As I was running the
#### land_value notebook, I noticed some hardcoding and duplicated code I thought
#### could be quick fixes to make the code DRYer. 

### Why were these sections good for modularization?
#### These were good sections for modularization because before they were distributed
#### across multiple cells in the notebook. Additionally, Kayleigh had already
#### worked out the code to do the plotting, so all that was required to modularize
#### was creation a function and for loop to apply it.

### How did these changes improve readability, maintainability, or efficiency?
#### These changes made the code more reproducible since now the user does not
#### need to hard code any file paths. Secondarily, it reduces the number of distinct
#### code cells in the notebook with copied and pasted code with only subtle
#### differences. It makes the code a little bit easier to read, and makes future 
#### plotting quicker.

### Additional opportunities for modularization to still implement.
#### If we still wanted to incorporte the GBIF data, we could modularize scripts
#### 02_gbif_animals.ipynb and 03_gbif_plants.ipynb into a single script. However,
#### we currently don't have plans to incorporate these data. One reproducability improvement
#### we noticed while completing this assignment was how we are downloading Weld Co.
#### parcel data (google drive vs. Weld Co. GIS). I recorded the issue in out GitHub and we plan to fix this before
#### the end of the project. https://github.com/maxwarnock/Pawnee-Grasslands-Project/issues/9