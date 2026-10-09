
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="FloodGuard AI",
    page_icon="🌊",
    layout="wide",
)

PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

st.title("🌊 FloodGuard AI")
st.subheader("Satellite-Based Flood Assessment")

st.write(
    "A prototype for satellite-based water mapping "
    "and road-accessibility assessment."
)

st.warning(
    "Preliminary water detection is not validated flood mapping. "
    "Confirm the imagery's band definitions and data scaling first."
)

raster_extensions = {".tif", ".tiff", ".img", ".jp2", ".vrt"}

if RAW_DIR.exists():
    raster_files = sorted(
        path for path in RAW_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in raster_extensions
    )
else:
    raster_files = []

col1, col2, col3 = st.columns(3)
col1.metric("Raster Files Found", len(raster_files))
col2.metric("Water Mapping", "Not run")
col3.metric("Road Assessment", "Not run")

st.header("Satellite Imagery Analysis")

if not raster_files:
    st.info(
        "No raster files found in data/raw. "
        "Place your downloaded satellite imagery there to continue."
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
        "Only proceed after confirming the green and NIR band numbers "
        "and that their pixel values are suitable for the water index."
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
                "Please verify the band mapping and data values first."
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
                st.metric(
                    "Valid Pixels",
                    results["valid_pixel_count"],
                )
                st.metric(
                    "Potential Water Pixels",
                    results["potential_water_pixel_count"],
                )
                st.image(
                    results["preview_path"],
                    caption="NDWI preview — not a validated flood map",
                )
                st.caption(
                    f"NDWI raster: {results['ndwi_path']}\n\n"
                    f"Potential-water mask: {results['mask_path']}"
                )
            except Exception as error:
                st.error(f"Analysis failed: {error}")

st.header("Next Steps")
st.markdown(
    """
    1. Verify satellite metadata and band definitions.
    2. Generate and inspect a preliminary water index.
    3. Validate water detections before interpreting flood extent.
    4. Add road-network analysis after suitable geographic data is available.
    """
)

st.caption(
    "Prototype only. No real flood results are claimed until "
    "the imagery has been processed and validated."
)
