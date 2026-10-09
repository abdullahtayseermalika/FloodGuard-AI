
from pathlib import Path

import numpy as np
import rasterio


def inspect_satellite_image(image_path):
    """Return basic metadata from a satellite raster."""
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Satellite image not found: {image_path}"
        )

    with rasterio.open(image_path) as dataset:
        return {
            "filename": image_path.name,
            "width": dataset.width,
            "height": dataset.height,
            "band_count": dataset.count,
            "crs": str(dataset.crs),
            "bounds": tuple(dataset.bounds),
            "data_type": dataset.dtypes,
            "nodata": dataset.nodata,
            "band_descriptions": dataset.descriptions,
        }


def read_band(image_path, band_number):
    """
    Read one raster band as float32, replacing invalid pixels
    with NaN. Band numbers are one-based, as in Rasterio.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Satellite image not found: {image_path}"
        )

    with rasterio.open(image_path) as dataset:
        if not 1 <= band_number <= dataset.count:
            raise ValueError(
                f"Band {band_number} is invalid. "
                f"This image contains {dataset.count} band(s)."
            )

        band = dataset.read(
            band_number,
            masked=True,
        ).astype(np.float32)

        return band.filled(np.nan)


def read_green_nir_bands(image_path, green_band_number, nir_band_number):
    """
    Read candidate green and NIR bands from one raster.

    The caller must verify band numbering from the product
    documentation before using these arrays for water detection.
    """
    green = read_band(image_path, green_band_number)
    nir = read_band(image_path, nir_band_number)

    if green.shape != nir.shape:
        raise ValueError(
            "Green and NIR bands have different dimensions."
        )

    return green, nir
