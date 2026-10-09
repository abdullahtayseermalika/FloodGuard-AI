
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="FloodGuard AI",
    page_icon="🌊",
    layout="wide",
)

PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

st.title("🌊 FloodGuard AI")
st.subheader("Satellite-Based Flood Assessment")

st.write(
    "A prototype for analysing satellite imagery, "
    "mapping potential surface water, and assessing "
    "road accessibility."
)

st.sidebar.header("Analysis Setup")
st.sidebar.info(
    "Satellite imagery is required before analysis can begin."
)

st.sidebar.text_input(
    "Study area",
    value="Eastern Odisha, India",
    disabled=True,
)

st.sidebar.selectbox(
    "Analysis method",
    options=[
        "Water-index baseline (NDWI)",
        "Temporal water comparison",
    ],
    index=0,
    help="The method will be used after the image bands are verified.",
)

st.header("Project Status")

col1, col2, col3 = st.columns(3)

raster_extensions = {".tif", ".tiff", ".img", ".jp2", ".vrt"}

if RAW_DIR.exists():
    raster_files = [
        path for path in RAW_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in raster_extensions
    ]
else:
    raster_files = []

col1.metric("Raster Files Found", len(raster_files))
col2.metric("Water Mapping", "Not run")
col3.metric("Road Assessment", "Not run")

st.header("Satellite Imagery")

if raster_files:
    st.success(f"Found {len(raster_files)} supported raster file(s).")

    selected_file = st.selectbox(
        "Choose a raster to inspect",
        options=raster_files,
        format_func=lambda path: str(path.relative_to(RAW_DIR)),
    )

    if st.button("Inspect image metadata"):
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
            st.error(f"Could not inspect the image: {error}")
else:
    st.warning(
        "No satellite raster files found. Place downloaded imagery "
        "inside data/raw/ to prepare for inspection."
    )

st.header("Analysis Workflow")

st.markdown(
    """
    1. Load and inspect satellite imagery.
    2. Verify band order, coordinate reference system, and nodata values.
    3. Calculate and review a preliminary water index.
    4. Validate potential water areas before interpreting them as floodwater.
    5. Overlay suitable road data to assess potential intersections.
    """
)

st.caption(
    "Prototype status: flood detection and road impact analysis "
    "have not yet been run or validated."
)
