
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import geopandas as gpd


def export_mask_to_geojson(mask_path, output_path):
    """
    Convert a georeferenced binary mask into GeoJSON polygons.

    Pixels with value 1 are exported as polygons.
    This represents potential water only, not confirmed flooding.
    """
    mask_path = Path(mask_path)
    output_path = Path(output_path)

    with rasterio.open(mask_path) as dataset:
        if dataset.crs is None:
            raise ValueError(
                "The mask has no coordinate reference system."
            )

        mask = dataset.read(1)
        valid = np.isfinite(mask) & (mask == 1)

        if not valid.any():
            raise ValueError(
                "The mask contains no potential-water pixels."
            )

        polygon_records = []

        for geometry, value in shapes(
            mask.astype(np.uint8),
            mask=valid,
            transform=dataset.transform,
        ):
            if value == 1:
                polygon_records.append(
                    {"geometry": shape(geometry), "class": "potential_water"}
                )

        if not polygon_records:
            raise ValueError("No polygons could be generated.")

        gdf = gpd.GeoDataFrame(
            polygon_records,
            geometry="geometry",
            crs=dataset.crs,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GeoJSON")

    return {
        "output_path": str(output_path),
        "polygon_count": len(gdf),
        "crs": str(gdf.crs),
    }
