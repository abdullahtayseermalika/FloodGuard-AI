
import numpy as np

from src.flood_detection import (
    calculate_water_index,
    classify_potential_water,
)


def main():
    # Artificial values for testing only.
    green = np.array([[0.8, 0.2], [0.4, 0.0]])
    nir = np.array([[0.2, 0.6], [0.4, 0.0]])

    ndwi = calculate_water_index(green, nir)

    # Expected NDWI: (green - NIR) / (green + NIR)
    assert np.isclose(ndwi[0, 0], 0.6)
    assert np.isclose(ndwi[0, 1], -0.5)
    assert np.isclose(ndwi[1, 0], 0.0)
    assert np.isnan(ndwi[1, 1])

    water_mask = classify_potential_water(ndwi, threshold=0.0)

    assert water_mask[0, 0]
    assert not water_mask[0, 1]
    assert not water_mask[1, 0]
    assert not water_mask[1, 1]

    print("PASS: Water-index calculation works.")
    print("PASS: Potential-water classification works.")
    print("NOTE: These are synthetic test values, not flood results.")


if __name__ == "__main__":
    main()
