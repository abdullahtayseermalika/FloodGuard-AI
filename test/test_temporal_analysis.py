
import numpy as np

from src.temporal_analysis import compare_water_indices


def main():
    earlier = np.array(
        [[-0.2, 0.3], [0.1, np.nan]],
        dtype=np.float32,
    )
    later = np.array(
        [[0.4, 0.1], [0.6, 0.2]],
        dtype=np.float32,
    )

    result = compare_water_indices(
        earlier,
        later,
        threshold=0.0,
    )

    assert result["valid_pixel_count"] == 3
    assert result["newly_detected_water_pixels"] == 1
    assert result["no_longer_detected_water_pixels"] == 0
    assert np.isclose(result["ndwi_change"][0, 0], 0.6)
    assert np.isnan(result["ndwi_change"][1, 1])

    try:
        compare_water_indices(
            np.zeros((2, 2)),
            np.zeros((3, 3)),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Different array shapes were not rejected")

    print("PASS: Temporal water-index comparison")
    print("PASS: Missing-pixel handling")
    print("PASS: Shape validation")
    print("NOTE: Synthetic arrays only; no flood results.")


if __name__ == "__main__":
    main()
