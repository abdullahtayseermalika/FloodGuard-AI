
import tempfile
from pathlib import Path

import numpy as np

from src.visualization import save_ndwi_preview


def main():
    ndwi = np.array(
        [
            [0.7, 0.4, -0.2],
            [0.1, np.nan, -0.6],
        ],
        dtype=np.float32,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "ndwi_preview.png"
        result = save_ndwi_preview(ndwi, output_path)

        assert result.exists()
        assert result.stat().st_size > 0

    print("PASS: NDWI preview image saved.")
    print("NOTE: Synthetic values only; not a flood map.")


if __name__ == "__main__":
    main()
