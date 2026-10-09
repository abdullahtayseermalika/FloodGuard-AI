
from pathlib import Path

import geopandas as gpd
import folium


def create_flood_map(
    geojson_path=None,
    output_html="data/processed/flood_map.html",
    center=(20.28, 86.85),
    zoom_start=9,
):
    """
    Create an interactive map for the eastern Odisha study area.

    If a GeoJSON file is supplied, its features are overlaid.
    The overlay represents potential water only, not validated floodwater.
    """
    map_object = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    folium.Marker(
        location=center,
        tooltip="Eastern Odisha study area",
        popup="FloodGuard AI study area — not a flood observation",
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(map_object)

    if geojson_path is not None:
        geojson_path = Path(geojson_path)

        if not geojson_path.exists():
            raise FileNotFoundError(
                f"GeoJSON file not found: {geojson_path}"
            )

        gdf = gpd.read_file(geojson_path)

        if gdf.crs is None:
            raise ValueError(
                "GeoJSON data has no coordinate reference system."
            )

        # Folium expects geographic coordinates (longitude, latitude).
        gdf = gdf.to_crs("EPSG:4326")

        folium.GeoJson(
            data=gdf.__geo_interface__,
            name="Potential water (unvalidated)",
            style_function=lambda feature: {
                "color": "#1565c0",
                "weight": 2,
                "fillColor": "#42a5f5",
                "fillOpacity": 0.4,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["class"] if "class" in gdf.columns else [],
            ) if "class" in gdf.columns else None,
        ).add_to(map_object)

        bounds = gdf.total_bounds
        if len(gdf) > 0:
            map_object.fit_bounds(
                [
                    [bounds[1], bounds[0]],
                    [bounds[3], bounds[2]],
                ]
            )

    folium.LayerControl().add_to(map_object)

    output_html = Path(output_html)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    map_object.save(str(output_html))

    return output_html
