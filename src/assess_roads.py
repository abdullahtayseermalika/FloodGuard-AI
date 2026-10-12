import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

print("Loading flood raster and road network...")

# Load road network
roads = gpd.read_file("data/raw/chennai_roads.geojson")

# Load flood raster and extract flood polygons (where pixel value == 255)
with rasterio.open("data/raw/Flood_Extent_Dec11.tif") as src:
    image = src.read(1)
    crs = src.crs
    
    # Extract geometries of flooded pixels
    results = (
        {'properties': {'raster_val': v}, 'geometry': s}
        for i, (s, v) in enumerate(shapes(image, mask=(image == 255), transform=src.transform))
    )
    
    geoms = list(results)
    
if not geoms:
    print("No flood features found in raster.")
    exit()

# Convert raster shapes to GeoDataFrame
flood_gdf = gpd.GeoDataFrame.from_features(geoms, crs=crs)

# Ensure matching coordinate reference systems (WGS84 / EPSG:4326 for Leaflet)
roads = roads.to_crs(epsg=4326)
flood_gdf = flood_gdf.to_crs(epsg=4326)

# Spatial overlay: find road segments that intersect flooded areas
print("Calculating flooded road intersections...")
flooded_roads = gpd.sjoin(roads, flood_gdf, how="inner", predicate="intersects")

# Save results to GeoJSON
output_path = "data/raw/flooded_roads.geojson"
flooded_roads.to_file(output_path, driver="GeoJSON")

total_roads = len(roads)
impacted_roads = len(flooded_roads)
percent_impacted = (impacted_roads / total_roads) * 100 if total_roads > 0 else 0

print("\n--- Assessment Results ---")
print(f"Total Main Road Segments Analyzed: {total_roads}")
print(f"Flooded Road Segments Identified: {impacted_roads} ({percent_impacted:.1f}%)")
print(f"Saved assessment map to {output_path}")
