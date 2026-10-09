import streamlit as st

st.set_page_config(
    page_title="FloodGuard AI",
    page_icon="🌊",
    layout="wide",
)

st.title("🌊 FloodGuard AI")
st.subheader("Satellite-Based Flood Assessment")

st.write(
    "An AI-powered prototype for analysing satellite imagery, "
    "mapping potential flood-affected areas, and assessing "
    "road accessibility."
)

st.info(
    "Satellite data processing is pending. "
    "Results will appear here after the imagery is loaded "
    "and analysed."
)

st.header("Project Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Satellite Images", "Pending")
col2.metric("Flood Mapping", "Pending")
col3.metric("Road Analysis", "Pending")

st.caption(
    "Prototype dashboard — flood detection is not yet implemented."
)

