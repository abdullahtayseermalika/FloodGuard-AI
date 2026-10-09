
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_origin

from src.vector_export import export_mask_to_geojson


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        mask_path = temp_dir / "synthetic_mask.tif"
        geojson_path = temp_dir / "potential_water.geojson"

        # Synthetic test mask: 1 = potential water, 0 = other.
        # These are not real satellite observations.
        mask = np.array(
            [
                [0, 1, 1],
                [0, 1, 0],
                [0, 0, 0],
            ],
            dtype=np.uint8,
        )

        # Create a small georeferenced test raster.
        with rasterio.open(
            mask_path,
            "w",
            driver="GTiff",
            height=3,
            width=3,
            count=1,
            dtype="uint8",
            crs="EPSG:4326",
            transform=from_origin(86.0, 21.0, 0.01, 0.01),
            nodata=255,
        ) as dataset:
            dataset.write(mask, 1)

        # Export potential-water pixels as GeoJSON polygons.
        result = export_mask_to_geojson(
            mask_path,
            geojson_path,
        )

        # Verify that the output was created.
        assert geojson_path.exists(), "GeoJSON file was not created"
        assert geojson_path.stat().st_size > 0, "GeoJSON file is empty"
        assert result["polygon_count"] >= 1, "No polygons were exported"

        # Compare coordinate reference systems correctly.
        actual_crs = CRS.from_user_input(result["crs"])
        expected_crs = CRS.from_epsg(4326)

        assert actual_crs == expected_crs, (
            f"Unexpected CRS: {result['crs']}"
        )

    print("PASS: GeoJSON file created")
    print("PASS: Potential-water polygons exported")
    print("PASS: Coordinate reference system preserved")
    print("NOTE: Synthetic mask only; not a real flood map.")


if __name__ == "__main__":
    main()
