
from pathlib import Path

import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="FloodGuard AI",
    page_icon="🌊",
    layout="wide",
)

PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
GEOJSON_PATH = OUTPUT_DIR / "potential_water.geojson"

STUDY_CENTER = [20.28, 86.85]
RASTER_EXTENSIONS = {".tif", ".tiff", ".img", ".jp2", ".vrt"}

st.title("🌊 FloodGuard AI")
st.subheader("Satellite-Based Flood Assessment")

st.write(
    "A prototype for satellite-based water mapping "
    "and road-accessibility assessment."
)

st.warning(
    "Preliminary water detection is not validated flood mapping. "
    "Verify image bands, data scaling, and image alignment before "
    "interpreting results."
)

# Discover supported raster files.
if RAW_DIR.exists():
    raster_files = sorted(
        path
        for path in RAW_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in RASTER_EXTENSIONS
    )
else:
    raster_files = []

# Dashboard metrics.
col1, col2, col3 = st.columns(3)
col1.metric("Raster Files Found", len(raster_files))
col2.metric(
    "Water Mapping",
    "Output available" if GEOJSON_PATH.exists() else "Not run",
)
col3.metric("Road Assessment", "Not run")

# Satellite image inspection and analysis.
st.header("Satellite Imagery Analysis")

if not raster_files:
    st.info(
        "No raster files found in data/raw. "
        "Place downloaded satellite imagery there to continue."
    )
else:
    selected_file = st.selectbox(
        "Select a raster image",
        raster_files,
        format_func=lambda path: str(path.relative_to(RAW_DIR)),
    )

    with st.expander("Inspect image metadata"):
        try:
            import rasterio

            with rasterio.open(selected_file) as dataset:
                st.json(
                    {
                        "filename": selected_file.name,
                        "width": dataset.width,
                        "height": dataset.height,
                        "band_count": dataset.count,
                        "crs": str(dataset.crs),
                        "bounds": list(dataset.bounds),
                        "data_types": list(dataset.dtypes),
                        "nodata": dataset.nodata,
                        "band_descriptions": list(dataset.descriptions),
                    }
                )
        except Exception as error:
            st.error(f"Metadata inspection failed: {error}")

    st.subheader("Preliminary NDWI Analysis")
    st.caption(
        "Use the band numbers documented for your specific satellite "
        "product. Do not assume the default band numbers are correct."
    )

    with st.form("analysis_form"):
        green_band = st.number_input(
            "Green band number (1-based)",
            min_value=1,
            value=1,
            step=1,
        )
        nir_band = st.number_input(
            "NIR band number (1-based)",
            min_value=1,
            value=2,
            step=1,
        )
        threshold = st.number_input(
            "Preliminary water-index threshold",
            min_value=-1.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
        )
        confirmed = st.checkbox(
            "I have verified the band numbers and data values "
            "from the product documentation."
        )
        submitted = st.form_submit_button("Run preliminary analysis")

    if submitted:
        if not confirmed:
            st.error(
                "Verify the band mapping and data values before analysis."
            )
        elif green_band == nir_band:
            st.error("Green and NIR must be different bands.")
        else:
            try:
                from src.analysis_pipeline import run_water_index_analysis

                with st.spinner("Processing raster..."):
                    results = run_water_index_analysis(
                        image_path=selected_file,
                        green_band_number=int(green_band),
                        nir_band_number=int(nir_band),
                        output_dir=OUTPUT_DIR,
                        threshold=float(threshold),
                    )

                st.success("Preliminary water-index analysis completed.")

                metric1, metric2 = st.columns(2)
                metric1.metric(
                    "Valid Pixels",
                    results["valid_pixel_count"],
                )
                metric2.metric(
                    "Potential Water Pixels",
                    results["potential_water_pixel_count"],
                )

                st.image(
                    results["preview_path"],
                    caption="NDWI preview — not a validated flood map",
                )
                st.caption(f"NDWI raster: {results['ndwi_path']}")
                st.caption(f"Potential-water mask: {results['mask_path']}")

                st.info(
                    "The analysis pipeline saves the raster mask. "
                    "Generate a GeoJSON separately before it can appear "
                    "as a polygon overlay below."
                )

            except Exception as error:
                st.error(f"Analysis failed: {error}")

# Interactive geographic map.
st.header("🗺️ Geographic View")

st.caption(
    "The marker is an approximate study-area reference. "
    "Any displayed polygons represent potential water, not confirmed flooding."
)

map_object = folium.Map(
    location=STUDY_CENTER,
    zoom_start=9,
    tiles="OpenStreetMap",
    control_scale=True,
)

folium.Marker(
    location=STUDY_CENTER,
    tooltip="Eastern Odisha study-area reference",
    popup="FloodGuard AI study area — not a flood observation",
    icon=folium.Icon(color="blue", icon="info-sign"),
).add_to(map_object)

if GEOJSON_PATH.exists():
    try:
        water_gdf = gpd.read_file(GEOJSON_PATH)

        if water_gdf.empty:
            st.info("The GeoJSON file contains no features.")
        elif water_gdf.crs is None:
            st.warning(
                "The GeoJSON has no CRS. The overlay cannot be displayed "
                "safely until its coordinate reference system is known."
            )
        else:
            water_gdf = water_gdf.to_crs("EPSG:4326")

            folium.GeoJson(
                data=water_gdf.__geo_interface__,
                name="Potential water (unvalidated)",
                style_function=lambda feature: {
                    "color": "#1565c0",
                    "weight": 2,
                    "fillColor": "#42a5f5",
                    "fillOpacity": 0.4,
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["class"],
                    aliases=["Classification:"],
                ) if "class" in water_gdf.columns else None,
            ).add_to(map_object)

            bounds = water_gdf.total_bounds
            folium_map_bounds = [
                [bounds[1], bounds[0]],
                [bounds[3], bounds[2]],
            ]
            map_object.fit_bounds(folium_map_bounds)

            st.success(
                f"Loaded {len(water_gdf)} potential-water feature(s)."
            )

    except Exception as error:
        st.error(f"Could not load the GeoJSON overlay: {error}")
else:
    st.info(
        "No potential-water GeoJSON is available yet. "
        "The map currently shows only the study-area reference."
    )

folium.LayerControl().add_to(map_object)

st_folium(
    map_object,
    width=None,
    height=500,
    key="floodguard_map",
)

# Project workflow.
st.header("Next Steps")
st.markdown(
    """
    1. Inspect the downloaded satellite metadata.
    2. Verify the green and NIR bands and their data scaling.
    3. Generate and review a preliminary water index.
    4. Validate potential water areas before interpreting flood extent.
    5. Load suitable road data and assess potential intersections.
    """
)

st.caption(
    "Prototype only. No real flood results or road-accessibility "
    "conclusions are claimed until the data has been processed and validated."
)
