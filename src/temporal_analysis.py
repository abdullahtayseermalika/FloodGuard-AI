
import numpy as np


def compare_water_indices(
    earlier_ndwi,
    later_ndwi,
    threshold=0.0,
):
    """
    Compare two NDWI arrays from aligned satellite scenes.

    Both arrays must cover the same area, use the same grid,
    and have comparable preprocessing and reflectance values.
    """
    earlier = np.asarray(earlier_ndwi, dtype=np.float32)
    later = np.asarray(later_ndwi, dtype=np.float32)

    if earlier.shape != later.shape:
        raise ValueError(
            "The two NDWI arrays must have the same shape."
        )

    valid = np.isfinite(earlier) & np.isfinite(later)

    earlier_water = earlier > threshold
    later_water = later > threshold

    newly_detected_water = (
        valid & ~earlier_water & later_water
    )
    no_longer_detected_water = (
        valid & earlier_water & ~later_water
    )

    change = np.full(earlier.shape, np.nan, dtype=np.float32)
    change[valid] = later[valid] - earlier[valid]

    valid_count = int(valid.sum())

    return {
        "ndwi_change": change,
        "newly_detected_water": newly_detected_water,
        "no_longer_detected_water": no_longer_detected_water,
        "valid_pixel_count": valid_count,
        "newly_detected_water_pixels": int(
            newly_detected_water.sum()
        ),
        "no_longer_detected_water_pixels": int(
            no_longer_detected_water.sum()
        ),
    }
