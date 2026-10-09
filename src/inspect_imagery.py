
from pathlib import Path
import json

import rasterio


DATA_DIR = Path("data/raw")


def inspect_image(image_path):
    """Return basic metadata for a satellite raster."""
    with rasterio.open(image_path) as dataset:
        return {
            "filename": image_path.name,
            "driver": dataset.driver,
            "width": dataset.width,
            "height": dataset.height,
            "band_count": dataset.count,
            "crs": str(dataset.crs),
            "bounds": list(dataset.bounds),
            "band_data_types": list(dataset.dtypes),
            "nodata": dataset.nodata,
            "band_descriptions": list(dataset.descriptions),
        }


def main():
    if not DATA_DIR.exists():
        print(f"Folder not found: {DATA_DIR.resolve()}")
        return

    supported_extensions = {
        ".tif", ".tiff", ".img", ".jp2", ".vrt"
    }

    files = sorted(
        path for path in DATA_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in supported_extensions
    )

    if not files:
        print(f"No supported raster files found in {DATA_DIR}.")
        print("Place your downloaded imagery there and run again.")
        return

    for image_path in files:
        print(f"\n--- {image_path} ---")
        try:
            metadata = inspect_image(image_path)
            print(json.dumps(metadata, indent=2))
        except Exception as error:
            print(f"Could not inspect file: {error}")


if __name__ == "__main__":
    main()
