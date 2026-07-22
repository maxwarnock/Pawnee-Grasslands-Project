# pyright: reportMissingImports=false, reportMissingModuleSource=false
from __future__ import annotations

import argparse
import base64
import gzip
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import geopandas as gpd
import networkx as nx
import nbformat
import numpy as np
import pandas as pd
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.ops import unary_union


#ACRES_PER_SQUARE_METER = 0.000247105
#PROXIMITY_RADIUS_M = 10000
AREA_TOLERANCE = 0.10
AREA_FLAG = 0.05
#MIN_SHARED_M = 1.0
SIZE_FLOOR_ACRES = 2000


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def classify_ownership(name: object) -> str:
    if name == "U S A":
        return "FEDERAL"
    if name == "COLORADO STATE OF":
        return "STATE"
    return "PRIVATE"


def as_geodataframe(
    frame: pd.DataFrame | gpd.GeoDataFrame,
    *,
    crs: Any = None,
) -> gpd.GeoDataFrame:
    target_crs = crs if crs is not None else getattr(frame, "crs", None)
    return gpd.GeoDataFrame(frame.copy(), geometry="geometry", crs=target_crs)


def repair_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    repaired = as_geodataframe(gdf)
    if hasattr(repaired.geometry, "make_valid"):
        repaired["geometry"] = repaired.geometry.make_valid()
    else:
        repaired["geometry"] = repaired.geometry.buffer(0)
    repaired = as_geodataframe(
        repaired.loc[repaired.geometry.notna() & ~repaired.geometry.is_empty],
        crs=repaired.crs,
    )
    return repaired


def ensure_full_boundary_layers(root: Path, force: bool = False) -> dict[str, gpd.GeoDataFrame]:
    boundary_processing_dir = root / "data" / "boundaries" / "boundary-data-processing"
    boundary_final_dir = root / "data" / "boundaries" / "boundary-data-final"

    master_out = boundary_final_dir / "master_boundary" / "pawnee_master.shp"
    federal_out = boundary_final_dir / "federal_boundary" / "pawnee_fed.shp"
    state_out = boundary_final_dir / "state_boundary" / "pawnee_state.shp"
    parcel_out = boundary_final_dir / "parcel_boundary" / "pawnee_parcel.shp"

    if not force and all(path.exists() for path in (master_out, federal_out, state_out, parcel_out)):
        return {
            "master": gpd.read_file(master_out),
            "federal": gpd.read_file(federal_out),
            "state": gpd.read_file(state_out),
            "parcel": gpd.read_file(parcel_out),
        }

    master_source = (
        boundary_processing_dir
        / "master_boundary"
        / "pawnee_master_boundary"
        / "pawnee_master_boundary.shp"
    )
    parcel_source = boundary_processing_dir / "county_parcels" / "Parcels_open_data.shp"

    master_gdf = repair_geometries(gpd.read_file(master_source).to_crs(epsg=4326))
    parcel_gdf = repair_geometries(gpd.read_file(parcel_source).to_crs(epsg=4326))
    parcel_gdf = repair_geometries(gpd.clip(parcel_gdf, master_gdf))

    federal_candidates = as_geodataframe(
        parcel_gdf.loc[parcel_gdf["NAME"] == "U S A"],
        crs=parcel_gdf.crs,
    )
    federal_gdf = repair_geometries(gpd.clip(federal_candidates, master_gdf))
    state_gdf = repair_geometries(
        gpd.clip(
            as_geodataframe(
                parcel_gdf.loc[parcel_gdf["NAME"] == "COLORADO STATE OF"],
                crs=parcel_gdf.crs,
            ),
            master_gdf,
        )
    )

    for path in (master_out, federal_out, state_out, parcel_out):
        path.parent.mkdir(parents=True, exist_ok=True)

    master_gdf.to_file(master_out)
    federal_gdf.to_file(federal_out)
    state_gdf.to_file(state_out)
    parcel_gdf.to_file(parcel_out)

    return {
        "master": master_gdf,
        "federal": federal_gdf,
        "state": state_gdf,
        "parcel": parcel_gdf,
    }


def calculate_contiguous_federal_areas(
    parcels_gdf: gpd.GeoDataFrame,
    ownership_col: str = "ownership",
    owner_label: str = "FEDERAL",
    parcel_id_col: str | None = None,
    gap_tolerance_m: float = 0.0,
    crs_projected: int = 5070,
) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    def interior_edge_length(geom_series: pd.Series) -> float:
        geoms = list(geom_series)
        if len(geoms) < 2:
            return 0.0

        total = 0.0
        for index_a in range(len(geoms)):
            for index_b in range(index_a + 1, len(geoms)):
                shared = geoms[index_a].boundary.intersection(geoms[index_b].boundary)
                if not shared.is_empty and shared.geom_type in ("LineString", "MultiLineString"):
                    total += shared.length
        return total

    gdf = repair_geometries(parcels_gdf.to_crs(epsg=crs_projected))

    if parcel_id_col is None:
        gdf = gdf.reset_index(drop=False).rename(columns={"index": "_parcel_id"})
        parcel_id_col = "_parcel_id"
    parcel_id_name = parcel_id_col

    federal = as_geodataframe(
        gdf.loc[gdf[ownership_col] == owner_label, [parcel_id_name, "geometry"]],
        crs=gdf.crs,
    )
    if federal.empty:
        raise ValueError(f"No parcels found where {ownership_col} == '{owner_label}'.")

    federal_original = federal.copy()

    if gap_tolerance_m > 0:
        federal = federal.copy()
        federal["geometry"] = federal.geometry.buffer(gap_tolerance_m)

    federal["_key"] = 1
    dissolved = federal.dissolve(by="_key")
    patches = dissolved.explode(index_parts=False).reset_index(drop=True)

    if gap_tolerance_m > 0:
        patches["geometry"] = patches.geometry.buffer(-gap_tolerance_m)

    patches = patches.drop(columns=["_key"], errors="ignore")
    patches["area_acres"] = patches.geometry.area * ACRES_PER_SQUARE_METER
    patches = patches.sort_values("area_acres", ascending=False).reset_index(drop=True)
    patches["contig_parcel_id"] = [f"PATCH_{index + 1:03d}" for index in range(len(patches))]
    patches["area_rank"] = range(1, len(patches) + 1)

    joined = gpd.sjoin(
        federal_original[[parcel_id_name, "geometry"]],
        patches[["contig_parcel_id", "geometry"]],
        how="left",
        predicate="within",
    )

    parcel_agg = (
        joined.groupby("contig_parcel_id")[parcel_id_name]
        .apply(lambda ids: ", ".join(str(value) for value in sorted(ids)))
        .reset_index()
        .rename(columns={parcel_id_name: "parcels"})
    )
    parcel_agg["n_parcels"] = parcel_agg["parcels"].str.split(", ").str.len()

    interior_lengths = (
        joined.groupby("contig_parcel_id")["geometry"]
        .apply(interior_edge_length)
        .reset_index()
        .rename(columns={"geometry": "_interior_edge_m"})
    )

    patches = patches.merge(interior_lengths, on="contig_parcel_id", how="left")
    patches["_interior_edge_m"] = patches["_interior_edge_m"].fillna(0.0)
    patches["interior_edge_ratio"] = (
        patches["_interior_edge_m"] / patches.geometry.length
    ).round(4).fillna(0.0)
    patches = patches.drop(columns=["_interior_edge_m"])
    patches = patches.merge(parcel_agg, on="contig_parcel_id", how="left")

    patches = gpd.GeoDataFrame(
        patches[
            [
                "contig_parcel_id",
                "area_rank",
                "area_acres",
                "n_parcels",
                "interior_edge_ratio",
                "parcels",
                "geometry",
            ]
        ],
        geometry="geometry",
        crs=f"EPSG:{crs_projected}",
    )

    total_acres = patches["area_acres"].sum()
    summary_df = pd.DataFrame(
        patches[
            ["contig_parcel_id", "area_rank", "area_acres", "n_parcels", "interior_edge_ratio"]
        ].copy()
    )
    summary_df["pct_of_total_federal"] = (patches["area_acres"] / total_acres * 100).round(2)

    return patches, summary_df

def ranked_proposals_csv_path(root: Path) -> Path:
    return root / "data" / "processed" / "parcel_swaps" / "pawnee_land_swap_proposals.csv"


def load_ranked_proposals(root: Path) -> tuple[pd.DataFrame, int | None]:
    """Load ranked swap proposals exported by notebook 08.

    Prefer the CSV written by ``08_parcel_matrix.ipynb`` so the full proposal
    set survives Jupyter stdout truncation. Fall back to scraping notebook
    stdout only if the CSV is missing.
    """
    csv_path = ranked_proposals_csv_path(root)
    if csv_path.exists():
        proposals_df = pd.read_csv(
            csv_path,
            dtype={
                "nf_parcel_id": "string",
                "release_parcel_id": "string",
                "receive_patch_id": "string",
                "release_patch_id": "string",
                "nf_ownership": "string",
                "nf_name": "string",
                "acquire_oil_gas_flag": "string",
                "release_oil_gas_flag": "string",
            },
        )
        if "rank" not in proposals_df.columns:
            raise ValueError(f"Expected a 'rank' column in {csv_path}.")

        proposals_df = proposals_df.sort_values("rank").reset_index(drop=True)
        proposals_df.index = proposals_df["rank"].astype(int)
        proposals_df = proposals_df.drop(columns=["rank"])

        bool_cols = ["bridges", "area_flag", "same_patch", "landowner_contiguity_gain"]
        for col in bool_cols:
            if col in proposals_df.columns:
                proposals_df[col] = proposals_df[col].fillna(False).astype(bool)

        for col in ("nf_name", "acquire_oil_gas_flag", "release_oil_gas_flag"):
            if col in proposals_df.columns:
                proposals_df[col] = [
                    None if pd.isna(value) else str(value)
                    for value in proposals_df[col].tolist()
                ]

        total_proposals = int(len(proposals_df))
        return proposals_df, total_proposals

    return load_ranked_proposals_from_notebook(root)


def load_ranked_proposals_from_notebook(root: Path) -> tuple[pd.DataFrame, int | None]:
    notebook_path = root / "code" / "08_parcel_matrix.ipynb"
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
        raise ValueError(
            "Could not find ranked proposals CSV at "
            f"{ranked_proposals_csv_path(root)} or ranked proposal output in "
            "code/08_parcel_matrix.ipynb. Re-run notebook 08 to export the CSV."
        )

    total_match = re.search(r"Total proposals found : (\d+)", output_text)
    total_proposals = int(total_match.group(1)) if total_match else None

    proposal_blocks = re.split(r"\n(?=\s+Proposal #\d+\s+\|)", output_text)
    proposals: list[dict[str, object]] = []

    for block in proposal_blocks:
        header = re.search(
            r"Proposal #(\d+)\s+\|\s+(PATCH_\d+)\s+\[(same-patch|cross-patch)\](\s+\[BRIDGE\])?",
            block,
        )
        if not header:
            continue

        receive_ratio = re.search(
            r"Receive patch ratio : ([\d.]+)\s+->\s+([\d.]+)\s+\(\+([\d.]+)\)",
            block,
        )
        acquire = re.search(
            r"Acquire\s+:\s+(STATE|PRIVATE)\s+parcel\s+(\d+)\s+\(([\d.]+)\s+ac\)",
            block,
        )
        release = re.search(
            r"Release\s+:\s+FEDERAL parcel\s+(\d+)\s+\(([\d.]+)\s+ac\)\s+from\s+(PATCH_\d+)",
            block,
        )
        area = re.search(r"Area difference\s+:\s+([\d.]+)%\s+\(([\d.]+)\s+ac\)", block)
        distance = re.search(r"Distance\s+:\s+([\d.]+)\s+km", block)
        release_ratio = re.search(r"Release patch ratio : ([\d.]+)\s+->\s+([\d.]+)", block)
        contiguity_gain = re.search(r"Contiguity gain\s+:\s+\+([\d.]+)\s+ac", block)
        exposure_delta = re.search(
            r"Parcel exposure delta:\s+([+\-][\d.]+)\s+\(acq ([\d.]+) / rel ([\d.]+)\)",
            block,
        )
        landowner = re.search(r"\[\+\] Landowner contiguity: (.+?) receives land", block)
        og_acq = re.search(r"\[OG-ACQ\] O&G activity on acquire parcel: (.+)", block)
        og_rel = re.search(r"\[OG-REL\] O&G activity on release parcel: (.+)", block)

        if (
            receive_ratio is None
            or acquire is None
            or release is None
            or area is None
            or distance is None
        ):
            continue

        same_patch = header.group(3) == "same-patch"
        old_ratio = float(receive_ratio.group(1))
        new_ratio = float(receive_ratio.group(2))

        proposals.append(
            {
                "rank": int(header.group(1)),
                "receive_patch_id": header.group(2),
                "bridges": header.group(4) is not None,
                "old_ratio": old_ratio,
                "new_ratio": new_ratio,
                "net_gain": float(receive_ratio.group(3)),
                "contiguity_gain_acres": float(contiguity_gain.group(1)) if contiguity_gain else None,
                "parcel_exposure_delta": float(exposure_delta.group(1)) if exposure_delta else None,
                "acq_fraction": float(exposure_delta.group(2)) if exposure_delta else None,
                "rel_fraction": float(exposure_delta.group(3)) if exposure_delta else None,
                "nf_parcel_id": acquire.group(2),
                "nf_ownership": acquire.group(1),
                "nf_acres": float(acquire.group(3)),
                "release_parcel_id": release.group(1),
                "release_patch_id": release.group(3),
                "fed_acres": float(release.group(2)),
                "area_diff_pct": float(area.group(1)),
                "area_flag": "[!]" in block,
                "distance_km": float(distance.group(1)),
                "same_patch": same_patch,
                "release_old_ratio": float(release_ratio.group(1)) if release_ratio else old_ratio,
                "release_new_ratio": float(release_ratio.group(2)) if release_ratio else new_ratio,
                "landowner_contiguity_gain": landowner is not None,
                "nf_name": landowner.group(1) if landowner else None,
                "acquire_oil_gas_flag": og_acq.group(1).strip() if og_acq else None,
                "release_oil_gas_flag": og_rel.group(1).strip() if og_rel else None,
            }
        )

    proposals_df = pd.DataFrame(proposals).sort_values("rank").reset_index(drop=True)
    proposals_df.index = proposals_df["rank"]
    proposals_df = proposals_df.drop(columns=["rank"])
    return proposals_df, total_proposals


def decode_bokeh_ndarray(spec: dict[str, Any]) -> np.ndarray:
    dtype = np.dtype(spec["dtype"])
    array_spec = spec["array"]

    if isinstance(array_spec, dict) and array_spec.get("type") == "bytes":
        raw = gzip.decompress(base64.b64decode(array_spec["data"]))
        array = np.frombuffer(raw, dtype=dtype)
    else:
        array = np.array(array_spec, dtype=dtype)

    shape = spec.get("shape")
    if shape:
        array = array.reshape(shape)

    return array


def decode_bokeh_value(value: object) -> object:
    if isinstance(value, dict) and value.get("type") == "ndarray":
        return decode_bokeh_ndarray(value)
    if isinstance(value, list):
        return [decode_bokeh_value(item) for item in value]
    return value


def extract_bokeh_sources(html_path: Path) -> list[dict[str, Any]]:
    html = html_path.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/json"[^>]*>\s*(\{.*\})\s*</script>', html, re.S)
    if not match:
        raise ValueError(f"Could not locate embedded Bokeh JSON in {html_path}.")

    document = next(iter(json.loads(match.group(1)).values()))
    sources: list[dict[str, Any]] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if node.get("name") == "ColumnDataSource":
                entries = node.get("attributes", {}).get("data", {}).get("entries", [])
                source: dict[str, Any] = {
                    entry[0]: decode_bokeh_value(entry[1])
                    for entry in entries
                    if isinstance(entry, list) and len(entry) == 2
                }
                sources.append(source)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(document)
    return sources


def find_bokeh_source(
    sources: list[dict[str, Any]],
    required_keys: set[str],
) -> dict[str, Any]:
    for source in sources:
        if required_keys.issubset(source.keys()):
            return source
    raise KeyError(f"Could not find embedded Bokeh source with keys: {sorted(required_keys)}")


def geometry_from_bokeh_coords(
    xs_parts: list[Any],
    ys_parts: list[Any],
) -> Polygon | MultiPolygon | None:
    polygons: list[Polygon] = []

    for polygon_xs, polygon_ys in zip(xs_parts, ys_parts):
        rings: list[list[tuple[float, float]]] = []
        for ring_xs, ring_ys in zip(polygon_xs, polygon_ys):
            x_values = np.asarray(ring_xs).tolist()
            y_values = np.asarray(ring_ys).tolist()
            coords = [(float(x), float(y)) for x, y in zip(x_values, y_values)]

            if len(coords) < 4:
                continue
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            rings.append(coords)

        if not rings:
            continue

        polygon = Polygon(rings[0], rings[1:])
        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if polygon.is_empty:
            continue
        if polygon.geom_type == "Polygon":
            polygons.append(polygon)
        elif polygon.geom_type == "MultiPolygon":
            polygons.extend(list(polygon.geoms))

    if not polygons:
        return None
    if len(polygons) == 1:
        return polygons[0]
    return MultiPolygon(polygons)


def geodataframe_from_bokeh_source(
    source: dict[str, Any],
    id_field: str,
    extra_fields: list[str],
) -> gpd.GeoDataFrame:
    rows: list[dict[str, Any]] = []
    geometries: list[Polygon | MultiPolygon] = []
    record_count = len(cast(list[Any], source[id_field]))

    for index in range(record_count):
        geometry = geometry_from_bokeh_coords(source["xs"][index], source["ys"][index])
        if geometry is None:
            continue

        rows.append(
            {
                id_field: source[id_field][index],
                **{field: source[field][index] for field in extra_fields},
            }
        )
        geometries.append(geometry)

    return gpd.GeoDataFrame(rows, geometry=geometries, crs="EPSG:3857")


def load_notebook_map_layers(
    root: Path,
    parcel_attributes_gdf: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    html_path = root / "figures" / "parcel_matrix" / "land_swap_proposals_interactive.html"
    sources = extract_bokeh_sources(html_path)

    parcel_source = find_bokeh_source(sources, {"xs", "ys", "PARCEL"})
    patch_source = find_bokeh_source(
        sources,
        {"xs", "ys", "contig_parcel_id", "area_acres", "n_parcels", "interior_fraction"},
    )

    parcel_map_gdf = geodataframe_from_bokeh_source(parcel_source, "PARCEL", [])
    parcel_attributes = parcel_attributes_gdf.drop(columns="geometry", errors="ignore").drop_duplicates(
        subset=["PARCEL"]
    )
    parcel_bound_gdf = parcel_map_gdf.merge(parcel_attributes, on="PARCEL", how="left")

    patches_gdf = geodataframe_from_bokeh_source(
        patch_source,
        "contig_parcel_id",
        ["area_acres", "n_parcels", "interior_fraction"],
    )
    patches_gdf["area_acres"] = patches_gdf["area_acres"].astype(float)
    patches_gdf["n_parcels"] = patches_gdf["n_parcels"].round().astype(int)
    patches_gdf["interior_fraction"] = patches_gdf["interior_fraction"].astype(float)
    patches_gdf = patches_gdf.sort_values("area_acres", ascending=False).reset_index(drop=True)
    patches_gdf["area_rank"] = range(1, len(patches_gdf) + 1)
    patches_gdf["parcels"] = None

    return parcel_bound_gdf, patches_gdf


def safe_float(value: object, digits: int | None = None) -> float | None:
    if value is None or pd.isna(value):
        return None
    number = float(value)
    return round(number, digits) if digits is not None else number


def ownership_from_owner_name(owner_name: object) -> str:
    value = str(owner_name).strip().upper()
    if value in {"U S A", "USA", "UNITED STATES", "UNITED STATES OF AMERICA"} or "UNITED STATES" in value:
        return "FEDERAL"
    if value == "COLORADO STATE OF" or "STATE OF COLORADO" in value:
        return "STATE"
    return "PRIVATE"


def owner_name_if_aligned(owner_name: object, ownership: str) -> str | None:
    if owner_name is None or pd.isna(owner_name):
        return None
    owner_name_str = str(owner_name)
    return owner_name_str if ownership_from_owner_name(owner_name_str) == ownership else None


def write_json(path: Path, payload: object) -> None:
    def _sanitize(obj: object) -> object:
        if isinstance(obj, float) and math.isnan(obj):
            return None
        if isinstance(obj, dict):
            return {k: _sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_sanitize(v) for v in obj]
        return obj

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_sanitize(payload), indent=2), encoding="utf-8")


def export_geojson(
    gdf: gpd.GeoDataFrame,
    path: Path,
    property_builder,
    columns: list[str],
) -> None:
    selected_columns = [column for column in columns if column in gdf.columns]
    geojson = json.loads(gdf[selected_columns + ["geometry"]].to_json())
    features = []
    for feature in geojson["features"]:
        properties = property_builder(feature["properties"])
        features.append(
            {
                "type": "Feature",
                "properties": properties,
                "geometry": feature["geometry"],
            }
        )
    write_json(path, {"type": "FeatureCollection", "features": features})


def export_site_data(
    root: Path,
    master_bound_gdf: gpd.GeoDataFrame,
    parcel_bound_gdf: gpd.GeoDataFrame,
    federal_patches_gdf: gpd.GeoDataFrame,
    proposals_df: pd.DataFrame,
    notebook_total_proposals: int | None,
) -> dict[str, object]:
    docs_data_dir = root / "docs" / "data"
    processed_swap_dir = root / "data" / "processed" / "parcel_swaps"
    contiguous_dir = root / "data" / "contiguous"

    docs_data_dir.mkdir(parents=True, exist_ok=True)
    processed_swap_dir.mkdir(parents=True, exist_ok=True)
    contiguous_dir.mkdir(parents=True, exist_ok=True)
    
    ### Note from Nate: I removed this because it was overwriting the fed patches
    ### from notebook 07. 
    #if not federal_patches_gdf.empty:
    #    federal_patches_path = contiguous_dir / "federal_patches.gpkg"
    #    federal_patches_gdf.to_file(federal_patches_path, driver="GPKG")

    proposals_export = proposals_df.reset_index().rename(columns={"index": "rank"})
    proposals_export.to_csv(processed_swap_dir / "pawnee_land_swap_proposals.csv", index=False)

    parcels_4326 = parcel_bound_gdf.to_crs(epsg=4326).copy()
    parcels_4326["ownership"] = parcels_4326["NAME"].apply(classify_ownership)

    land_values_path = root / "data" / "processed" / "land_values" / "pawnee_parcels_land_values.geojson"
    if land_values_path.exists():
        land_values = gpd.read_file(land_values_path)
        land_values = land_values[
            [
                "PARCEL",
                "clip_acres_est",
                "value_per_gis_acre",
                "value_per_clipped_acre",
            ]
        ].drop_duplicates(subset=["PARCEL"])
        parcels_4326 = parcels_4326.merge(land_values, on="PARCEL", how="left")

    parcel_centroids = parcels_4326.geometry.representative_point()
    centroid_lookup: dict[str, list[float]] = {}
    for parcel_id, point in zip(parcels_4326["PARCEL"], parcel_centroids, strict=False):
        if not isinstance(point, Point):
            raise TypeError(f"Representative point for parcel {parcel_id} is not a Point.")
        centroid_lookup[str(parcel_id)] = [round(float(point.y), 6), round(float(point.x), 6)]

    patch_lookup: dict[str, dict[str, Any]] = {
        str(row["contig_parcel_id"]): cast(dict[str, Any], row.to_dict())
        for _, row in federal_patches_gdf.to_crs(epsg=4326).iterrows()
    }
    parcel_lookup: dict[str, dict[str, Any]] = {
        str(row["PARCEL"]): cast(dict[str, Any], row.to_dict())
        for _, row in parcels_4326.iterrows()
    }

    acquire_meta: defaultdict[str, dict[str, Any]] = defaultdict(
        lambda: {"proposalRanks": [], "receivePatches": set(), "bestRank": None, "bestNetGain": None}
    )
    release_meta: defaultdict[str, dict[str, Any]] = defaultdict(
        lambda: {"proposalRanks": [], "releasePatches": set(), "bestRank": None, "bestNetGain": None}
    )
    notebook_acquire_ownership: dict[str, str] = {}
    notebook_release_ownership: dict[str, str] = {}

    proposals_payload: list[dict[str, Any]] = []
    for rank, row in proposals_df.iterrows():
        rank_int = int(rank)
        receive_patch_id = str(row["receive_patch_id"])
        release_patch_id = str(row["release_patch_id"])
        acquire_parcel_id = str(row["nf_parcel_id"])
        release_parcel_id = str(row["release_parcel_id"])
        acquire_ownership = str(row["nf_ownership"])
        net_gain = float(row["net_gain"])

        acquire = acquire_meta[acquire_parcel_id]
        cast(list[int], acquire["proposalRanks"]).append(rank_int)
        cast(set[str], acquire["receivePatches"]).add(receive_patch_id)
        acquire_best_rank = cast(int | None, acquire["bestRank"])
        acquire["bestRank"] = rank_int if acquire_best_rank is None else min(acquire_best_rank, rank_int)
        acquire_best_gain = cast(float | None, acquire["bestNetGain"])
        acquire["bestNetGain"] = (
            net_gain
            if acquire_best_gain is None
            else max(acquire_best_gain, net_gain)
        )
        notebook_acquire_ownership[acquire_parcel_id] = acquire_ownership

        release = release_meta[release_parcel_id]
        cast(list[int], release["proposalRanks"]).append(rank_int)
        cast(set[str], release["releasePatches"]).add(release_patch_id)
        release_best_rank = cast(int | None, release["bestRank"])
        release["bestRank"] = rank_int if release_best_rank is None else min(release_best_rank, rank_int)
        release_best_gain = cast(float | None, release["bestNetGain"])
        release["bestNetGain"] = (
            net_gain
            if release_best_gain is None
            else max(release_best_gain, net_gain)
        )
        notebook_release_ownership[release_parcel_id] = "FEDERAL"

        receive_patch = patch_lookup.get(receive_patch_id)
        release_patch = patch_lookup.get(release_patch_id)
        acquire_parcel = parcel_lookup[acquire_parcel_id]
        release_parcel = parcel_lookup[release_parcel_id]

        proposals_payload.append(
            {
                "rank": rank_int,
                "receivePatchId": receive_patch_id,
                "receivePatchAreaAcres": safe_float(receive_patch["area_acres"], 1) if receive_patch is not None else None,
                "receivePatchParcelCount": int(receive_patch["n_parcels"]) if receive_patch is not None else None,
                "oldRatio": safe_float(row["old_ratio"], 4),
                "newRatio": safe_float(row["new_ratio"], 4),
                "netGain": safe_float(net_gain, 4),
                "acquireParcelId": acquire_parcel_id,
                "acquireOwnership": acquire_ownership,
                "acquireOwnerName": owner_name_if_aligned(acquire_parcel.get("NAME"), acquire_ownership),
                "acquireAcres": safe_float(row["nf_acres"], 1),
                "acquireValuePerAcre": safe_float(acquire_parcel.get("value_per_clipped_acre"), 2),
                "acquireCentroid": centroid_lookup[acquire_parcel_id],
                "releaseParcelId": release_parcel_id,
                "releasePatchId": release_patch_id,
                "releasePatchAreaAcres": safe_float(release_patch["area_acres"], 1) if release_patch is not None else None,
                "releaseOwnerName": owner_name_if_aligned(release_parcel.get("NAME"), "FEDERAL"),
                "releaseAcres": safe_float(row["fed_acres"], 1),
                "releaseValuePerAcre": safe_float(release_parcel.get("value_per_clipped_acre"), 2),
                "releaseCentroid": centroid_lookup[release_parcel_id],
                "areaDiffPct": safe_float(row["area_diff_pct"], 1),
                "areaFlag": bool(row["area_flag"]),
                "distanceKm": safe_float(row["distance_km"], 2),
                "samePatch": bool(row["same_patch"]),
                "releaseOldRatio": safe_float(row["release_old_ratio"], 4),
                "releaseNewRatio": safe_float(row["release_new_ratio"], 4),
                "bridges": bool(row.get("bridges", False)),
                "contiguityGainAcres": safe_float(row.get("contiguity_gain_acres"), 1),
                "parcelExposureDelta": safe_float(row.get("parcel_exposure_delta"), 4),
                "acqFraction": safe_float(row.get("acq_fraction"), 4),
                "relFraction": safe_float(row.get("rel_fraction"), 4),
                "landownerContiguityGain": bool(row.get("landowner_contiguity_gain", False)),
                "nfName": row.get("nf_name"),
                "acquireOilGasFlag": row.get("acquire_oil_gas_flag") or None,
                "releaseOilGasFlag": row.get("release_oil_gas_flag") or None,
            }
        )

    for meta in acquire_meta.values():
        meta["receivePatches"] = sorted(cast(set[str], meta["receivePatches"]))
        meta["bestNetGain"] = safe_float(meta["bestNetGain"], 4)
    for meta in release_meta.values():
        meta["releasePatches"] = sorted(cast(set[str], meta["releasePatches"]))
        meta["bestNetGain"] = safe_float(meta["bestNetGain"], 4)

    export_geojson(
        master_bound_gdf.to_crs(epsg=4326),
        docs_data_dir / "master-boundary.geojson",
        lambda props: {
            "name": props.get("Location") or "Pawnee National Grassland",
        },
        columns=["Location"] if "Location" in master_bound_gdf.columns else [],
    )

    export_geojson(
        federal_patches_gdf.to_crs(epsg=4326),
        docs_data_dir / "federal-patches.geojson",
        lambda props: {
            "patchId": props["contig_parcel_id"],
            "areaRank": int(props["area_rank"]),
            "areaAcres": safe_float(props["area_acres"], 1),
            "parcelCount": int(props["n_parcels"]),
            "interiorEdgeRatio": safe_float(props["interior_fraction"], 4),
            "isReceiveCandidate": bool(
                props["n_parcels"] > 1 and float(props["area_acres"]) >= SIZE_FLOOR_ACRES
            ),
        },
        columns=["contig_parcel_id", "area_rank", "area_acres", "n_parcels", "interior_fraction"],
    )

    export_geojson(
        parcels_4326,
        docs_data_dir / "parcels.geojson",
        lambda props: {
            "parcelId": props["PARCEL"],
            "ownerName": owner_name_if_aligned(
                props.get("NAME"),
                notebook_acquire_ownership.get(props["PARCEL"])
                or notebook_release_ownership.get(props["PARCEL"])
                or props["ownership"],
            ),
            "ownership": (
                notebook_acquire_ownership.get(props["PARCEL"])
                or notebook_release_ownership.get(props["PARCEL"])
                or props["ownership"]
            ),
            "gisAcres": safe_float(props.get("GIS_Acres"), 1),
            "clipAcres": safe_float(props.get("clip_acres_est"), 1),
            "totalAct": safe_float(props.get("TOTALACT"), 0),
            "landAsd": safe_float(props.get("LANDASD"), 0),
            "valuePerGisAcre": safe_float(props.get("value_per_gis_acre"), 2),
            "valuePerClippedAcre": safe_float(props.get("value_per_clipped_acre"), 2),
            "candidateRole": (
                "acquire"
                if props["PARCEL"] in acquire_meta
                else "release" if props["PARCEL"] in release_meta else "none"
            ),
            "proposalRanks": (
                acquire_meta[props["PARCEL"]]["proposalRanks"]
                if props["PARCEL"] in acquire_meta
                else release_meta[props["PARCEL"]]["proposalRanks"]
                if props["PARCEL"] in release_meta
                else []
            ),
            "bestRank": (
                acquire_meta[props["PARCEL"]]["bestRank"]
                if props["PARCEL"] in acquire_meta
                else release_meta[props["PARCEL"]]["bestRank"]
                if props["PARCEL"] in release_meta
                else None
            ),
            "bestNetGain": (
                acquire_meta[props["PARCEL"]]["bestNetGain"]
                if props["PARCEL"] in acquire_meta
                else release_meta[props["PARCEL"]]["bestNetGain"]
                if props["PARCEL"] in release_meta
                else None
            ),
        },
        columns=[
            "PARCEL",
            "NAME",
            "ownership",
            "GIS_Acres",
            "clip_acres_est",
            "TOTALACT",
            "LANDASD",
            "value_per_gis_acre",
            "value_per_clipped_acre",
        ],
    )

    summary = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "parcelCount": int(len(parcels_4326)),
        "federalParcelCount": int((parcels_4326["ownership"] == "FEDERAL").sum()),
        "stateParcelCount": int((parcels_4326["ownership"] == "STATE").sum()),
        "privateParcelCount": int((parcels_4326["ownership"] == "PRIVATE").sum()),
        "patchCount": int(len(federal_patches_gdf)),
        "proposalCount": int(len(proposals_payload)),
        "notebookProposalCount": notebook_total_proposals,
        "samePatchCount": int((proposals_export["same_patch"] == True).sum()),
        "crossPatchCount": int((proposals_export["same_patch"] == False).sum()),
        "uniqueAcquireCandidates": int(len(acquire_meta)),
        "uniqueReleaseCandidates": int(len(release_meta)),
        "topNetGain": safe_float(proposals_export["net_gain"].max() if not proposals_export.empty else None, 4),
        "topProposalRank": int(cast(int, proposals_payload[0]["rank"])) if proposals_payload else None,
        "bridgeProposalCount": int((proposals_export.get("bridges", pd.Series(dtype=bool)) == True).sum()),
        "landownerContiguityCount": int((proposals_export.get("landowner_contiguity_gain", pd.Series(dtype=bool)) == True).sum()),
        "acquireOilGasCount": int(proposals_export.get("acquire_oil_gas_flag", pd.Series(dtype=object)).notna().sum()),
        "releaseOilGasCount": int(proposals_export.get("release_oil_gas_flag", pd.Series(dtype=object)).notna().sum()),
    }

    write_json(docs_data_dir / "proposals.json", proposals_payload)
    write_json(docs_data_dir / "summary.json", summary)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Pawnee parcel swap GitHub Pages app.")
    parser.add_argument(
        "--force-boundaries",
        action="store_true",
        help="Rebuild the full boundary-data-final layers even if they already exist.",
    )
    args = parser.parse_args()

    root = repo_root()
    layers = ensure_full_boundary_layers(root, force=args.force_boundaries)
    parcel_bound_gdf, federal_patches_gdf = load_notebook_map_layers(root, layers["parcel"])
    parcel_bound_gdf["ownership"] = parcel_bound_gdf["NAME"].apply(classify_ownership)

    proposals_df, notebook_total_proposals = load_ranked_proposals(root)
    summary = export_site_data(
        root=root,
        master_bound_gdf=layers["master"],
        parcel_bound_gdf=parcel_bound_gdf,
        federal_patches_gdf=federal_patches_gdf,
        proposals_df=proposals_df,
        notebook_total_proposals=notebook_total_proposals,
    )

    print(f"Built full-boundary parcel swap site data in {root / 'docs'}.")
    print(f"Parcels: {summary['parcelCount']}")
    print(f"Patches: {summary['patchCount']}")
    print(f"Swap proposals: {summary['proposalCount']}")


if __name__ == "__main__":
    main()
