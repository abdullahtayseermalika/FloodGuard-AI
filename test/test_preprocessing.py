
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.preprocessing import (
    inspect_satellite_image,
    read_band,
    read_green_nir_bands,
)


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = Path(temp_dir) / "synthetic.tif"

        # Artificial two-band raster, not real satellite data.
        data = np.array(
            [
                [[10, 20], [30, -9999]],
                [[40, 50], [60, 70]],
            ],
            dtype=np.float32,
        )

        with rasterio.open(
            image_path,
            "w",
            driver="GTiff",
            height=2,
            width=2,
            count=2,
            dtype="float32",
            crs="EPSG:4326",
            transform=from_origin(86.0, 21.0, 0.01, 0.01),
            nodata=-9999,
        ) as dataset:
            dataset.write(data)
            dataset.set_band_description(1, "Synthetic Green")
            dataset.set_band_description(2, "Synthetic NIR")

        metadata = inspect_satellite_image(image_path)
        assert metadata["width"] == 2
        assert metadata["height"] == 2
        assert metadata["band_count"] == 2
        assert metadata["crs"] == "EPSG:4326"

        green = read_band(image_path, 1)
        assert green[0, 0] == 10
        assert np.isnan(green[1, 1])

        green, nir = read_green_nir_bands(image_path, 1, 2)
        assert green.shape == nir.shape == (2, 2)
        assert nir[0, 0] == 40

        try:
            read_band(image_path, 3)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid band number was not rejected")

    print("PASS: Raster metadata inspection")
    print("PASS: Band reading and NoData handling")
    print("PASS: Green/NIR array shape check")
    print("PASS: Invalid band number validation")
    print("NOTE: Synthetic raster only; no flood results.")


if __name__ == "__main__":
    main()
