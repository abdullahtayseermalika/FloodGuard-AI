import geopandas as gpd


def load_vector_data(file_path):
    """
    Load geographic vector data such as roads or settlements.
    Supports formats readable by GeoPandas, such as GeoJSON
    and Shapefile.
    """
    data = gpd.read_file(file_path)

    if data.crs is None:
        raise ValueError(
            "The geographic dataset has no CRS defined."
        )

    return data


def count_roads_intersecting_flood(
    roads,
    flood_area,
):
    """
    Count road features that intersect a potential flood area.

    roads and flood_area must be GeoDataFrames with compatible
    coordinate reference systems.
    """
    if roads.crs != flood_area.crs:
        roads = roads.to_crs(flood_area.crs)

    flood_geometry = flood_area.geometry.union_all()

    affected = roads.geometry.intersects(flood_geometry)

    return {
        "total_road_features": len(roads),
        "intersecting_road_features": int(affected.sum()),
        "affected_roads": roads.loc[affected].copy(),
    }
