import os
import glob
import tempfile
import streamlit as st
import rasterio
import rasterio.features
import numpy as np
import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import FastMarkerCluster, MeasureControl, MiniMap

# Page Configuration
st.set_page_config(
    page_title="FloodGuard AI | Dynamic Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Tactical UI Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700;800&display=swap');

    .stApp {
        background-color: #0b0e14 !important;
        color: #e6edf3 !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(11, 14, 20, 0.8) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #21262d !important;
    }

    iframe {
        background-color: #0d1117 !important;
        border: 2px solid #1f6beb !important;
        border-radius: 12px !important;
        box-shadow: 0 0 20px rgba(31, 107, 235, 0.25), 
                    inset 0 0 15px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        display: block !important;
    }

    iframe:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.4), 
                    inset 0 0 20px rgba(0, 0, 0, 0.6) !important;
    }

    div[data-testid="stComponentV1"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        background-color: #0d1117 !important;
        line-height: 0 !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background-color: #161b22 !important;
        border: 1px dashed #30363d !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }

    h1, h2, h3, .pulse-badge, div[data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: -0.02em !important;
    }

    div[data-testid="stMetric"] {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 14px !important;
        padding: 18px 22px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.25s ease-in-out !important;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        border-color: #58a6ff !important;
    }

    .pulse-badge {
        display: inline-block;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 20px;
        animation: pulse-glow 2s infinite ease-in-out;
    }

    @keyframes pulse-glow {
        0% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); }
        70% { box-shadow: 0 0 0 8px rgba(56, 189, 248, 0); }
        100% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); }
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
        padding: 8px 12px !important;
        background: #161b22 !important;
        border-radius: 16px !important;
        border: 1px solid #30363d !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px !important;
        padding: 0px 20px !important;
        background-color: transparent !important;
        border-radius: 10px !important;
        border: 1px solid transparent !important;
        color: #8b949e !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        transition: all 0.25s ease-in-out !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(31, 111, 235, 0.2) !important;
        color: #58a6ff !important;
        border: 1px solid #1f6beb !important;
        box-shadow: 0 0 12px rgba(31, 111, 235, 0.3) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1f6beb 0%, #38bdf8 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }

    .stDataFrame {
        border-radius: 12px !important;
        border: 1px solid #21262d !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper Function to Inject Full-Height CSS Rules & Invert Tiles for Dark Aesthetic
def render_folium_map(folium_map, height=520):
    map_html = folium_map._repr_html_()
    custom_css = """
    <style>
        html, body { margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; background-color: #0d1117; }
        .folium-map { height: 100% !important; width: 100% !important; position: absolute; top: 0; bottom: 0; left: 0; right: 0; }
        /* Apply high-contrast dark filter to free OpenStreetMap tiles */
        .leaflet-tile-container img {
            filter: brightness(0.6) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) !important;
        }
    </style>
    """
    full_html = map_html.replace("<head>", f"<head>{custom_css}")
    st.components.v1.html(full_html, height=height)

st.markdown('### 🛡️ FloodGuard AI <span class="pulse-badge">LIVE TACTICAL COMMAND CENTER</span>', unsafe_allow_html=True)
st.caption("Emergency Operations & Automated Spatial Intelligence Engine")

raw_dir = "data/raw"
tif_files = glob.glob(os.path.join(raw_dir, "*.tif")) + glob.glob(os.path.join(raw_dir, "*.jp2"))
tif_names = [os.path.basename(f) for f in tif_files]

st.sidebar.markdown("### ⚙️ Operational Settings")
uploaded_file = st.sidebar.file_uploader("Upload Any GeoTIFF Flood Image (.tif)", type=["tif", "tiff", "jp2"])

default_before = "Nov16_stacked_small.tif" if "Nov16_stacked_small.tif" in tif_names else (tif_names[0] if tif_names else "None")
default_after = "Flood_Extent_Dec11.tif" if "Flood_Extent_Dec11.tif" in tif_names else default_before

before_image = st.sidebar.selectbox("Baseline (BEFORE) Raster", tif_names, index=tif_names.index(default_before) if default_before in tif_names else 0)

if uploaded_file is None:
    after_image = st.sidebar.selectbox("Post-Event (AFTER) Raster", tif_names, index=tif_names.index(default_after) if default_after in tif_names else 0)
else:
    after_image = uploaded_file.name

road_geojson_path = os.path.join(raw_dir, "flooded_roads.geojson")
isolated_geojson_path = os.path.join(raw_dir, "isolated_zones.geojson")
priority_geojson_path = os.path.join(raw_dir, "rescue_priority_zones.geojson")
infra_geojson_path = os.path.join(raw_dir, "critical_infrastructure.geojson")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Tactical Layer Toggles")
show_flooded_roads = st.sidebar.checkbox("Flooded Road Networks", value=os.path.exists(road_geojson_path))
show_isolated = st.sidebar.checkbox("🚨 Severed / Cut-Off Communities", value=os.path.exists(isolated_geojson_path))
show_priority_zones = st.sidebar.checkbox("🔥 Rescue Priority Grid", value=os.path.exists(priority_geojson_path))
show_infrastructure = st.sidebar.checkbox("🏥 Infrastructure Clusters", value=os.path.exists(infra_geojson_path))

st.sidebar.markdown("---")
water_threshold = st.sidebar.slider("Water Detection Sensitivity Threshold", min_value=1, max_value=255, value=10)

def clean_spatial_indexes(gdf):
    cols_to_drop = [c for c in ['index_right', 'index_left'] if c in gdf.columns]
    if cols_to_drop:
        return gdf.drop(columns=cols_to_drop)
    return gdf

def process_dynamic_raster_and_calculate_impact(source_path, threshold):
    with rasterio.open(source_path) as src:
        band = src.read(1)
        mask = (band >= threshold).astype(np.uint8)
        
        pixel_count = int(np.sum(mask))
        res_x, res_y = abs(src.transform.a), abs(src.transform.e)
        pixel_area_sqm = res_x * res_y if res_x > 0 else 100.0
        flooded_area_sqkm = (pixel_count * pixel_area_sqm) / 1e6
        
        shapes = ({'properties': {'flood': 1}, 'geometry': geom} 
                  for geom, val in rasterio.features.shapes(mask, mask=(mask == 1), transform=src.transform))
        shape_list = list(shapes)
        
        if not shape_list:
            return None, 0.0, 0, [13.0827, 80.2707], None, None, None
            
        flood_gdf = gpd.GeoDataFrame.from_features(shape_list, crs=src.crs).to_crs(epsg=4326)
        flood_gdf = clean_spatial_indexes(flood_gdf)
        flood_gdf['geometry'] = flood_gdf.geometry.simplify(0.001)
        centroid = flood_gdf.geometry.unary_union.centroid
        map_center = [centroid.y, centroid.x]
        
        impacted_infra = None
        if os.path.exists(infra_geojson_path):
            all_infra = gpd.read_file(infra_geojson_path).to_crs(epsg=4326)
            all_infra = clean_spatial_indexes(all_infra)
            impacted_infra = gpd.sjoin(all_infra, flood_gdf, how="inner", predicate="intersects")
            
        impacted_roads = None
        if os.path.exists(road_geojson_path):
            all_roads = gpd.read_file(road_geojson_path).to_crs(epsg=4326)
            all_roads = clean_spatial_indexes(all_roads)
            impacted_roads = gpd.sjoin(all_roads, flood_gdf, how="inner", predicate="intersects")
            
        dynamic_priority = None
        if os.path.exists(priority_geojson_path):
            all_prio = gpd.read_file(priority_geojson_path).to_crs(epsg=4326)
            all_prio = clean_spatial_indexes(all_prio)
            prio_joined = gpd.sjoin(all_prio, flood_gdf, how="inner", predicate="intersects")
            
            if not prio_joined.empty:
                dynamic_priority = prio_joined.copy()
                dynamic_priority['dynamic_boats'] = (dynamic_priority['rescue_score'] // 4 + 1).astype(int)
                dynamic_priority['dynamic_drones'] = dynamic_priority['isolated_cluster_count'].apply(lambda x: 2 if x > 0 else 1)
                
        return flood_gdf.__geo_interface__, flooded_area_sqkm, pixel_count, map_center, impacted_infra, impacted_roads, dynamic_priority

after_geojson = None
flooded_sqkm = 0.0
total_pixels = 0
map_center = [13.0827, 80.2707]
impacted_infra_gdf = None
impacted_roads_gdf = None
dynamic_priority_gdf = None

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    after_geojson, flooded_sqkm, total_pixels, map_center, impacted_infra_gdf, impacted_roads_gdf, dynamic_priority_gdf = process_dynamic_raster_and_calculate_impact(tmp_path, water_threshold)
    os.remove(tmp_path)
else:
    default_raster_path = os.path.join(raw_dir, after_image)
    if os.path.exists(default_raster_path):
        after_geojson, flooded_sqkm, total_pixels, map_center, impacted_infra_gdf, impacted_roads_gdf, dynamic_priority_gdf = process_dynamic_raster_and_calculate_impact(default_raster_path, water_threshold)

total_hospitals_flooded = len(impacted_infra_gdf[impacted_infra_gdf['facility_type'] == 'Hospital / Healthcare']) if impacted_infra_gdf is not None and not impacted_infra_gdf.empty and 'facility_type' in impacted_infra_gdf.columns else 0
total_power_flooded = len(impacted_infra_gdf[impacted_infra_gdf['facility_type'] == 'Power Substation']) if impacted_infra_gdf is not None and not impacted_infra_gdf.empty and 'facility_type' in impacted_infra_gdf.columns else 0
total_roads_flooded = len(impacted_roads_gdf) if impacted_roads_gdf is not None else 0
total_boats_required = int(dynamic_priority_gdf['dynamic_boats'].sum()) if dynamic_priority_gdf is not None else 0
total_drones_required = int(dynamic_priority_gdf['dynamic_drones'].sum()) if dynamic_priority_gdf is not None else 0

st.markdown("---")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Flooded Extent", f"{flooded_sqkm:.2f} km²", f"{total_pixels:,} Water Pixels")
kpi2.metric("Inundated Roads", f"{total_roads_flooded:,} Segments", "Road Network Impact")
kpi3.metric("At-Risk Hospitals", f"{total_hospitals_flooded} Facilities", "Critical Medical Nodes", delta_color="inverse")
kpi4.metric("NDRF Boats Needed", f"{total_boats_required} Fleet Units", "Required Rescue Craft")
kpi5.metric("Recon Drones Needed", f"{total_drones_required} Drones", "Target Recon Fleet")

st.markdown("---")

tab_map, tab_infra, tab_analytics, tab_manifest = st.tabs([
    "🗺️ Operational Map Center", 
    "🏥 Critical Infrastructure Alert Panel",
    "📊 Dynamic Risk & Asset Analytics", 
    "📄 Field Dispatch Manifest"
])

# TAB 1: OPERATIONAL MAP CENTER (100% FREE OPENSTREETMAP TILES)
with tab_map:
    map_col1, map_col2 = st.columns(2)

    with map_col1:
        st.subheader(f"📷 Pre-Event Baseline: {before_image}")
        m_before = folium.Map(
            location=map_center, 
            zoom_start=11, 
            tiles="OpenStreetMap"
        )
        folium.LayerControl().add_to(m_before)
        render_folium_map(m_before, height=520)

    with map_col2:
        st.subheader(f"🌊 Live Image Flood Tracking: {after_image}")
        m_after = folium.Map(
            location=map_center, 
            zoom_start=11, 
            tiles="OpenStreetMap"
        )
        
        MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m_after)
        MiniMap(toggle_display=True, tile_layer="OpenStreetMap", position="bottomright").add_to(m_after)

        if after_geojson:
            folium.GeoJson(
                after_geojson, 
                name="Detected Flood Waters", 
                style_function=lambda x: {
                    "fillColor": "#00e5ff", 
                    "color": "#0099ff", 
                    "weight": 1.0, 
                    "fillOpacity": 0.55
                }
            ).add_to(m_after)

        if show_priority_zones and dynamic_priority_gdf is not None and not dynamic_priority_gdf.empty:
            def priority_style(feature):
                score = feature['properties']['rescue_score']
                color = "#ff4d4d" if score > 15 else ("#ffaa00" if score > 7 else "#00ccff")
                return {
                    "fillColor": color, 
                    "color": color, 
                    "weight": 1.5, 
                    "fillOpacity": 0.18,
                    "dashArray": "3, 3"
                }

            folium.GeoJson(
                dynamic_priority_gdf.__geo_interface__,
                name="Inundated Priority Sectors",
                style_function=priority_style,
                tooltip=folium.GeoJsonTooltip(
                    fields=["area_name", "priority_level", "rescue_score", "dynamic_boats", "dynamic_drones"],
                    aliases=["Sector:", "Priority Level:", "RPI Score:", "Required Boats:", "Required Drones:"]
                )
            ).add_to(m_after)

        if show_flooded_roads and impacted_roads_gdf is not None and not impacted_roads_gdf.empty:
            clean_roads = impacted_roads_gdf[[c for c in ['name', 'highway', 'geometry'] if c in impacted_roads_gdf.columns]]
            folium.GeoJson(
                clean_roads.__geo_interface__, 
                name="Flooded Roads", 
                style_function=lambda x: {
                    "color": "#ff0055", 
                    "weight": 2.5, 
                    "opacity": 0.95
                }
            ).add_to(m_after)

        if show_infrastructure and impacted_infra_gdf is not None and not impacted_infra_gdf.empty:
            points = []
            for _, row in impacted_infra_gdf.iterrows():
                if row.geometry.geom_type == 'Point':
                    points.append([row.geometry.y, row.geometry.x])
            if points:
                FastMarkerCluster(data=points, name="At-Risk Infrastructure Clusters").add_to(m_after)

        folium.LayerControl().add_to(m_after)
        render_folium_map(m_after, height=520)

# TAB 2: CRITICAL INFRASTRUCTURE ALERT PANEL
with tab_infra:
    st.subheader("🏥 Critical Infrastructure Exposure Analysis")
    
    if impacted_infra_gdf is not None and not impacted_infra_gdf.empty and 'facility_type' in impacted_infra_gdf.columns:
        c_hosp, c_pow = st.columns(2)
        with c_hosp:
            st.markdown(f"### 🏥 Inundated Hospitals ({total_hospitals_flooded})")
            hosp_df = impacted_infra_gdf[impacted_infra_gdf['facility_type'] == 'Hospital / Healthcare']
            if not hosp_df.empty:
                st.dataframe(hosp_df[['name', 'facility_type']].reset_index(drop=True), use_container_width=True, height=400)
            else:
                st.info("No hospital facilities intersected by the current flood extent.")

        with c_pow:
            st.markdown(f"### ⚡ Inundated Power Substations ({total_power_flooded})")
            pow_df = impacted_infra_gdf[impacted_infra_gdf['facility_type'] == 'Power Substation']
            if not pow_df.empty:
                st.dataframe(pow_df[['name', 'facility_type']].reset_index(drop=True), use_container_width=True, height=400)
            else:
                st.info("No power grid nodes intersected by the current flood extent.")
    else:
        st.success("Zero critical infrastructure elements detected within the active flood boundary.")

# TAB 3: ANALYTICS LEADERBOARD
with tab_analytics:
    st.subheader("🚨 Dynamic Priority Dispatch Target Leaderboard")
    
    if dynamic_priority_gdf is not None and not dynamic_priority_gdf.empty:
        top_targets = dynamic_priority_gdf.sort_values(by="rescue_score", ascending=False)
        display_df = pd.DataFrame({
            "Target Locality": top_targets["area_name"],
            "Priority Level": top_targets["priority_level"],
            "Rescue Priority Score": top_targets["rescue_score"].round(2),
            "Submerged Roads (km)": top_targets["flooded_road_km"].round(2),
            "Cut-Off Pockets": top_targets["isolated_cluster_count"],
            "Required NDRF Boats": top_targets["dynamic_boats"],
            "Required Recon Drones": top_targets["dynamic_drones"]
        })
        st.dataframe(display_df.reset_index(drop=True), use_container_width=True)
    else:
        st.info("Upload a flood image to trigger dynamic priority sector calculations.")

# TAB 4: FIELD DISPATCH MANIFEST
with tab_manifest:
    st.subheader("📄 Dynamic First-Responder Field Manifest")
    
    if dynamic_priority_gdf is not None and not dynamic_priority_gdf.empty:
        export_df = dynamic_priority_gdf.sort_values(by="rescue_score", ascending=False)
        export_df['centroid_lat'] = export_df.geometry.centroid.y
        export_df['centroid_lon'] = export_df.geometry.centroid.x
        
        csv_data = pd.DataFrame({
            "Sector_Name": export_df["area_name"],
            "Priority_Level": export_df["priority_level"],
            "RPI_Score": export_df["rescue_score"].round(2),
            "Latitude": export_df["centroid_lat"].round(5),
            "Longitude": export_df["centroid_lon"].round(5),
            "Required_Boats": export_df["dynamic_boats"],
            "Required_Drones": export_df["dynamic_drones"],
            "Submerged_Roads_KM": export_df["flooded_road_km"].round(2)
        }).to_csv(index=False)
        
        st.download_button(
            label="📥 Download Real-Time NDRF Tactical Manifest (CSV)",
            data=csv_data,
            file_name="Dynamic_Flood_Dispatch_Manifest.csv",
            mime="text/csv",
            type="primary"
        )