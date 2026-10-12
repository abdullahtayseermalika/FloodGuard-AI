import geopandas as gpd
import pandas as pd
from shapely.geometry import box

print("Calculating Rescue Priority Index and identifying target locality names...")

# 1. Load datasets
flooded_roads = gpd.read_file("data/raw/flooded_roads.geojson").to_crs(epsg=32644)
isolated_zones = gpd.read_file("data/raw/isolated_zones.geojson").to_crs(epsg=32644)

# Load full road network to extract locality/area names if available
roads = gpd.read_file("data/raw/chennai_roads.geojson").to_crs(epsg=32644)

# 2. Build Spatial Analysis Grid (2km x 2km)
minx, miny, maxx, maxy = flooded_roads.total_bounds
grid_cells = []
step = 2000

for x in range(int(minx), int(maxx), step):
    for y in range(int(miny), int(maxy), step):
        grid_cells.append(box(x, y, x + step, y + step))

grid = gpd.GeoDataFrame({'geometry': grid_cells}, crs="EPSG:32644")

# 3. Calculate spatial metrics
grid['flooded_road_km'] = grid.geometry.apply(
    lambda cell: flooded_roads[flooded_roads.intersects(cell)].geometry.intersection(cell).length.sum() / 1000.0
)

grid['isolated_cluster_count'] = grid.geometry.apply(
    lambda cell: len(isolated_zones[isolated_zones.intersects(cell)])
)

# 4. Extract dominant area name within each grid sector
def extract_area_name(cell):
    intersecting_roads = roads[roads.intersects(cell)]
    if 'name' in intersecting_roads.columns and not intersecting_roads['name'].dropna().empty:
        # Get most common street/area landmark in this sector
        names = intersecting_roads['name'].dropna().value_counts()
        if not names.empty:
            return names.index[0]
    return "Unknown / Unnamed Sector"

grid['area_name'] = grid.geometry.apply(extract_area_name)

# 5. Calculate Rescue Score & Filter Priority Zones
grid['rescue_score'] = (grid['flooded_road_km'] * 2.0) + (grid['isolated_cluster_count'] * 5.0)
priority_grid = grid[grid['rescue_score'] > 0].copy().to_crs(epsg=4326)

def get_priority_label(score):
    if score > 15: return "🔴 CRITICAL (High Priority)"
    elif score > 7: return "🟠 HIGH (Medium Priority)"
    else: return "🟡 MODERATE (Standard Patrol)"

priority_grid['priority_level'] = priority_grid['rescue_score'].apply(get_priority_label)

# Save processed GeoJSON
priority_grid.to_file("data/raw/rescue_priority_zones.geojson", driver="GeoJSON")
print(f"Generated {len(priority_grid)} sectors with localized area names.")