# Requires: pip install pyproj
from pyproj import CRS, Transformer

def projected_bbox_to_latlon(minx, miny, maxx, maxy,
                             proj_string=None,
                             use_wkt=None,
                             input_units=None,
                             target_epsg=4269,
                             auto_detect_units=True):
    """
    Convert a projected bbox to geographic lat/lon corners.

    Parameters
    ----------
    minx, miny, maxx, maxy : float
        Projected bounding box coordinates (in the units of the source CRS or as raw values).
    proj_string : str or None
        A proj4 string (or other proj4-like string) describing the source CRS.
        If None and use_wkt provided, the WKT will be used instead.
    use_wkt : str or None
        If provided, this WKT string will be used to construct the source CRS.
    input_units : str or None
        If 'm' or 'meters' coordinates are treated as metres.
        If 'ft' or 'feet' coordinates are treated as feet and converted to metres before transform.
        If None and auto_detect_units True, the function heuristically decides based on coordinate magnitude.
    target_epsg : int
        EPSG code of desired geographic CRS (default 4269 = NAD83). Use 4326 for WGS84 if you prefer.
    auto_detect_units : bool
        If True, and input_units is None, detect feet vs metres by magnitude.

    Returns
    -------
    dict with keys: sw, nw, se, ne each = (lat, lon) in decimal degrees for target_epsg
    """

    # Build source CRS
    if use_wkt is not None:
        src_crs = CRS.from_wkt(use_wkt)
    elif proj_string is not None:
        src_crs = CRS.from_proj4(proj_string)
    else:
        raise ValueError("Provide either proj_string or use_wkt for the source CRS.")

    # Heuristic for units if not provided
    if input_units is None and auto_detect_units:
        # If coordinates are very large (>1e5), they are probably in feet (or large meters),
        # but NC State Plane coordinates ~2e6 are definitely in feet in some datasets.
        # We'll assume feet when X or Y exceed 1e6 (safe for typical state plane).
        if max(abs(minx), abs(miny), abs(maxx), abs(maxy)) > 1_000_000:
            detected = 'ft'
        else:
            detected = 'm'
        input_units = detected

    # If coordinates are in feet, convert to metres for PROJ if the proj uses metres
    # (we'll convert them to metres unconditionally when user indicates 'ft').
    if input_units and input_units.lower().startswith('ft'):
        # Convert US survey feet / feet to meters using 0.3048 (exact for international foot).
        # If your data are US-survey-feet and you need exact US survey conversion (1 ftUS = 1200/3937 m),
        # replace 0.3048 with 1200.0/3937.0. Most workflows use 0.3048.
        ft_to_m = 0.3048
        minx_m, miny_m, maxx_m, maxy_m = (minx * ft_to_m, miny * ft_to_m, maxx * ft_to_m, maxy * ft_to_m)
    else:
        minx_m, miny_m, maxx_m, maxy_m = float(minx), float(miny), float(maxx), float(maxy)

    # Create transformer: from source proj (assumed metres) to geographic target
    tgt_crs = CRS.from_epsg(target_epsg)   # 4269 NAD83 or 4326 WGS84
    transformer = Transformer.from_crs(src_crs, tgt_crs, always_xy=True)

    # Transform corner points (always pass as (x, y))
    sw_lon, sw_lat = transformer.transform(minx_m, miny_m)
    nw_lon, nw_lat = transformer.transform(minx_m, maxy_m)
    se_lon, se_lat = transformer.transform(maxx_m, miny_m)
    ne_lon, ne_lat = transformer.transform(maxx_m, maxy_m)

    # Return (lat, lon) tuples to match common expectations
    return {
        "sw": (sw_lat, sw_lon),
        "nw": (nw_lat, nw_lon),
        "se": (se_lat, se_lon),
        "ne": (ne_lat, ne_lon)
    }


def latlon_to_projected_meters(lat, lon,
                               proj_string=None,
                               use_wkt=None,
                               source_epsg=4269):
    """
    Convert latitude/longitude (degrees) into projected coordinates in meters,
    using the same CRS as the original .las file.

    Parameters
    ----------
    lat, lon : float
        Geographic coordinates (decimal degrees)
    proj_string : str
        Proj4 string defining the target *projected* CRS
    use_wkt : str
        Optional WKT string if you want to define CRS via WKT
    source_epsg : int
        Geographic CRS (4269 = NAD83, 4326 = WGS84)

    Returns
    -------
    (x_m, y_m) : tuple(float, float)
        Projected CRS coordinates in meters.
    """

    # Build target CRS (projected)
    if use_wkt is not None:
        target_crs = CRS.from_wkt(use_wkt)
    elif proj_string is not None:
        target_crs = CRS.from_proj4(proj_string)
    else:
        raise ValueError("Must provide either proj_string or use_wkt.")

    # Build source geographic CRS (lat/lon)
    src_crs = CRS.from_epsg(source_epsg)

    # lat/lon → projected (meters)
    transformer = Transformer.from_crs(src_crs, target_crs, always_xy=True)

    # Important: PROJ expects arguments as (lon, lat)
    x_m, y_m = transformer.transform(lon, lat)

    return x_m, y_m


# -------------------------
# Example usage with your metadata values:
if __name__ == "__main__":
    # Converting lake wheeler lat/lon to meters

    proj4 = (
        "+proj=lcc +lat_0=33.75 +lon_0=-79 "
        "+lat_1=36.1666666666667 +lat_2=34.3333333333333 "
        "+x_0=609601.219202438 +y_0=0 "
        "+datum=NAD83 +units=m +no_defs"
    )

    lw_lat = 35.732880950294145
    lw_lon = -78.68793530804957

    x_m, y_m = latlon_to_projected_meters(lw_lat, lw_lon, proj_string=proj4)
    print("Projected X (m):", x_m * 3.28084)
    print("Projected Y (m):", y_m * 3.28084)

    exit()

    # Projected bounds from your metadata
    minx = 2084029.28
    miny = 716721.51
    maxx = 2093400.94
    maxy = 726246.03

    # Use PROJ string from your metadata (example)
    proj4 = ("+proj=lcc +lat_0=33.75 +lon_0=-79 "
             "+lat_1=36.1666666666667 +lat_2=34.3333333333333 "
             "+x_0=609601.219202438 +y_0=0 +datum=NAD83 +units=m +no_defs")

    # Because the coordinates in the LAS header are likely in US feet, instruct the function:
    result = projected_bbox_to_latlon(minx, miny, maxx, maxy,
                                      proj_string=proj4,
                                      input_units='ft',         # <-- IMPORTANT: set to 'ft' if values are in feet
                                      target_epsg=4269)         # NAD83 lat/lon

    print("SW (lat,lon):", result["sw"])
    print("NW (lat,lon):", result["nw"])
    print("SE (lat,lon):", result["se"])
    print("NE (lat,lon):", result["ne"])

    # If you want WGS84 instead:
    result_wgs84 = projected_bbox_to_latlon(minx, miny, maxx, maxy,
                                      proj_string=proj4,
                                      input_units='ft',
                                      target_epsg=4326)
    print("SW WGS84 (lat,lon):", result_wgs84["sw"])
