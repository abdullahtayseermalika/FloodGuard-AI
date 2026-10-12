import geopandas as gpd

print("Calculating network isolation and severed communities...")

roads = gpd.read_file("data/raw/chennai_roads.geojson").to_crs(epsg=4326)
flooded_roads = gpd.read_file("data/raw/flooded_roads.geojson").to_crs(epsg=4326)

print("Removing flooded road geometries from total network...")
operational_roads = gpd.overlay(roads, flooded_roads, how='difference')

union_geom = operational_roads.geometry.unary_union
components = list(union_geom.geoms) if hasattr(union_geom, 'geoms') else [union_geom]

isolated_clusters = []
for idx, comp in enumerate(components):
    # Filter: Only highlight substantial severed pockets (~1.5 km to 8 km)
    if 0.015 < comp.length < 0.08:
        isolated_clusters.append({
            "cluster_id": idx,
            "geometry": comp,
            "status": "Cut Off / Isolated"
        })

if isolated_clusters:
    isolated_gdf = gpd.GeoDataFrame(isolated_clusters, crs="EPSG:4326")
    isolated_gdf.to_file("data/raw/isolated_zones.geojson", driver="GeoJSON")
    print(f"Refined count: Identified {len(isolated_gdf)} major isolated community zones.")