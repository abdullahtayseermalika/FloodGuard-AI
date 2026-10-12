import rasterio
import numpy as np

# File paths
nov_path = "data/raw/Nov16_stacked_small.tif"
dec_path = "data/raw/Dec11_stacked_small.tif"
output_path = "data/raw/Flood_Extent_Dec11.tif"

# Function to calculate NDWI
def calculate_ndwi(green, nir):
    np.seterr(divide='ignore', invalid='ignore')
    ndwi = (green.astype(float) - nir.astype(float)) / (green.astype(float) + nir.astype(float))
    return np.nan_to_num(ndwi, nan=-1.0)

with rasterio.open(nov_path) as src_nov, rasterio.open(dec_path) as src_dec:
    # Read Green (Band 1) and NIR (Band 2)
    green_nov, nir_nov = src_nov.read(1), src_nov.read(2)
    green_dec, nir_dec = src_dec.read(1), src_dec.read(2)
    
    # Compute NDWI masks (> 0 threshold)
    water_nov = calculate_ndwi(green_nov, nir_nov) > 0.0
    water_dec = calculate_ndwi(green_dec, nir_dec) > 0.0
    
    # Isolate strictly NEW flooded pixels
    flood_mask = water_dec & (~water_nov)
    
    # Save output as a single-band boolean mask GeoTIFF
    meta = src_dec.meta.copy()
    meta.update({"count": 1, "dtype": "uint8"})
    
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(flood_mask.astype(np.uint8), 1)

print(f"Successfully generated flood difference map: {output_path}")
