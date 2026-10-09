import numpy as np


def calculate_water_index(green_band, nir_band):
    """
    Calculate a normalized difference water index (NDWI).

    green_band and nir_band must be aligned arrays
    containing reflectance values from the same scene.
    """
    green = np.asarray(green_band, dtype=np.float32)
    nir = np.asarray(nir_band, dtype=np.float32)

    denominator = green + nir

    ndwi = np.full(green.shape, np.nan, dtype=np.float32)

    valid = (
        np.isfinite(green)
        & np.isfinite(nir)
        & (denominator != 0)
    )

    ndwi[valid] = (
        green[valid] - nir[valid]
    ) / denominator[valid]

    return ndwi


def classify_potential_water(ndwi, threshold=0.0):
    """
    Create a preliminary mask of potential surface water.

    This is a baseline, not a validated flood detector.
    """
    ndwi = np.asarray(ndwi, dtype=np.float32)

    return np.isfinite(ndwi) & (ndwi > threshold)
