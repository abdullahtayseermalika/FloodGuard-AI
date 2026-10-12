import glob
import rasterio
from rasterio.enums import Resampling

# Locate the December 11 Green (B03) and NIR (B08) files
green_paths = glob.glob("data/raw/*20231211*B03_10m.jp2")
nir_paths = glob.glob("data/raw/*20231211*B08_10m.jp2")

if not green_paths or not nir_paths:
    print("Error: Could not find December 11 JP2 files in data/raw/")
    exit()

green_path = green_paths[0]
nir_path = nir_paths[0]
output_path = "data/raw/Dec11_stacked_small.tif"

scale_factor = 0.2  # Downsize to 2Replace the contents of `src/stack_bands.py` with this complete code:

import glob
import rasterio
from rasterio.enums import Resampling

# Auto-detect Dec 11 files in data/raw/
green_path = glob.glob("data/raw/*20231211*B03_10m.jp2")[0]
nir_path = glob.glob("data/raw/*20231211*B08_10m.jp2")[0]
output_path = "data/raw/Dec11_stacked_small.tif"

scale_factor = 0.2  # Downsize to 20% to save memory

with rasterio.open(green_path) as src_green:
    new_width = int(src_green.width * scale_factor)
    new_height = int(src_green.height * scale_factor)
    
    green_data = src_green.read(1, out_shape=(new_height, new_width), resampling=Resampling.bilinear)
    
    transform = src_green.transform * src_green.transform.scale(
        (src_green.width / green_data.shape[-1]),
        (src_green.height / green_data.shape[-2])
    )
    
    meta = src_green.meta.copy()
    meta.update({
        "driver": "GTiff",
        "count": 2,
        "height": new_height,
        "width": new_width,
        "transform": transform
    })
    
    with rasterio.open(nir_path) as src_nir:
        nir_data = src_nir.read(1, out_shape=(new_height, new_width), resampling=Resampling.bilinear)
        
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(green_data, 1)
            dst.write(nir_data, 2)

print(f"Successfully stacked and resized into {output_path}")