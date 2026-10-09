from pathlib import Path

import rasterio


def inspect_satellite_image(image_path):
    """
    Read basic metadata from a satellite raster image.
    """
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
        }

