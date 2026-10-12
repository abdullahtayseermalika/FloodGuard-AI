import pandas as pd
import geopandas as gpd

def generate_dispatch_manifest(priority_geojson_path, output_csv_path="data/raw/dispatch_manifest.csv"):
    """
    Generates a structured field manifest for emergency response units.
    """
    if not gpd.os.path.exists(priority_geojson_path):
        return None
    
    p_gdf = gpd.read_file(priority_geojson_path)
    p_gdf['centroid_lat'] = p_gdf.geometry.centroid.y
    p_gdf['centroid_lon'] = p_gdf.geometry.centroid.x
    
    manifest_df = p_gdf.sort_values(by="rescue_score", ascending=False).copy()
    
    # Calculate recommended assets
    manifest_df['Recommended Boats'] = manifest_df['rescue_score'].apply(lambda score: int(score // 5) + 1)
    manifest_df['Recommended Drone Squads'] = manifest_df['isolated_cluster_count'].apply(lambda count: 1 if count > 0 else 0)
    
    output_df = pd.DataFrame({
        "Sector Name": manifest_df["area_name"],
        "Priority Rating": manifest_df["priority_level"],
        "RPI Score": manifest_df["rescue_score"].round(2),
        "Latitude": manifest_df["centroid_lat"].round(5),
        "Longitude": manifest_df["centroid_lon"].round(5),
        "Flooded Roads (km)": manifest_df["flooded_road_km"].round(2),
        "Severed Zones": manifest_df["isolated_cluster_count"],
        "Req. Inflatable Boats": manifest_df["Recommended Boats"],
        "Req. Drone Recon": manifest_df["Recommended Drone Squads"]
    })
    
    output_df.to_csv(output_csv_path, index=False)
    return output_df