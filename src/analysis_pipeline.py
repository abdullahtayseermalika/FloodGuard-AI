
from pathlib import Path

import numpy as np
import rasterio

from src.flood_detection import (
    calculate_water_index,
    classify_potential_water,
)
from src.preprocessing import read_green_nir_bands
from src.visualization import save_ndwi_preview


def run_water_index_analysis(
    image_path,
    green_band_number,
    nir_band_number,
    output_dir="data/processed",
    threshold=0.0,
):
    """
    Calculate a preliminary water index from a verified raster.

    Band numbers must be confirmed from the satellite product
    documentation. A water mask is not automatically a flood map.
    """
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    green, nir = read_green_nir_bands(
        image_path,
        green_band_number,
        nir_band_number,
    )

    ndwi = calculate_water_index(green, nir)
    water_mask = classify_potential_water(ndwi, threshold=threshold)

    with rasterio.open(image_path) as source:
        profile = source.profile.copy()
        profile.update(
            driver="GTiff",
            count=1,
            dtype="float32",
            nodata=np.nan,
        )

        ndwi_path = output_dir / f"{image_path.stem}_ndwi.tif"
        with rasterio.open(ndwi_path, "w", **profile) as destination:
            destination.write(ndwi.astype(np.float32), 1)
            destination.set_band_description(1, "NDWI")

        mask_profile = profile.copy()
        mask_profile.update(dtype="uint8", nodata=255)

        mask_path = output_dir / f"{image_path.stem}_potential_water.tif"
        with rasterio.open(mask_path, "w", **mask_profile) as destination:
            destination.write(water_mask.astype(np.uint8), 1)
            destination.set_band_description(
                1, "Potential water mask (1=yes, 0=no)"
            )

    preview_path = output_dir / f"{image_path.stem}_ndwi_preview.png"
    save_ndwi_preview(ndwi, preview_path)

    return {
        "ndwi_path": str(ndwi_path),
        "mask_path": str(mask_path),
        "preview_path": str(preview_path),
        "valid_pixel_count": int(np.isfinite(ndwi).sum()),
        "potential_water_pixel_count": int(water_mask.sum()),
        "threshold": threshold,
    }
