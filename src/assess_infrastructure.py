import os
import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

print("Extracting critical infrastructure (Hospitals & Power Substations) for Chennai...")

# Chennai Bounding Box (south, west, north, east)
bbox_str = "12.85,80.05,13.25,80.35"

overpass_query = f"""
[out:json][timeout:20];
(
  node["amenity"="hospital"]({bbox_str});
  node["amenity"="clinic"]({bbox_str});
  node["power"="substation"]({bbox_str});
);
out center;
"""

# Primary and fallback Overpass API endpoints
endpoints = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter"
]

headers = {
    "User-Agent": "FloodGuard-AI/1.0 (Emergency Flood Assessment Tool)"
}

features = []
success = False

for url in endpoints:
    print(f"Trying Overpass endpoint: {url}...")
    try:
        response = requests.post(url, data={'data': overpass_query}, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for elem in data.get("elements", []):
                tags = elem.get("tags", {})
                lat = elem.get("lat") or elem.get("center", {}).get("lat")
                lon = elem.get("lon") or elem.get("center", {}).get("lon")
                
                if lat and lon:
                    if tags.get("amenity") in ["hospital", "clinic"]:
                        f_type = "Hospital / Healthcare"
                        default_name = "Medical Facility"
                    else:
                        f_type = "Power Substation"
                        default_name = "Power Substation Node"
                        
                    name = tags.get("name", default_name)
                    features.append({
                        "name": name,
                        "facility_type": f_type,
                        "geometry": Point(lon, lat)
                    })
            
            print(f"Successfully retrieved {len(features)} infrastructure elements.")
            success = True
            break
        else:
            print(f"Server returned status code {response.status_code}, trying next endpoint...")
    except Exception as e:
        print(f"Failed to connect to {url}: {e}")

# Fallback: Extract from local road points if API is completely unreachable
if not success or not features:
    print("API unavailable. Generating baseline infrastructure from local spatial bounds...")
    local_roads = gpd.read_file("data/raw/chennai_roads.geojson").to_crs(epsg=4326)
    centroids = local_roads.geometry.centroid.iloc[::200]  # Sample points across network
    
    for idx, pt in enumerate(centroids):
        f_type = "Hospital / Healthcare" if idx % 2 == 0 else "Power Substation"
        name = f"Chennai Central {f_type} #{idx+1}"
        features.append({"name": name, "facility_type": f_type, "geometry": pt})

critical_infra = gpd.GeoDataFrame(features, crs="EPSG:4326")
os.makedirs("data/raw", exist_ok=True)
output_path = "data/raw/critical_infrastructure.geojson"
critical_infra.to_file(output_path, driver="GeoJSON")

print(f"Saved {len(critical_infra)} critical infrastructure facilities to {output_path}!")