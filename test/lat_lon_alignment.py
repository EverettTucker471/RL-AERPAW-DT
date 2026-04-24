from pyproj import Transformer
from pyproj.enums import TransformDirection
from typing import Optional, Dict, Tuple

from sionna.rt import load_scene

# This should be the reference frame such that everything is correct
# It should be the real-world lat/lon/alt coordinates of (0, 0, 0) in the Sionna world
ORIGIN_LAT_LON: Dict[str, float] = {"lat": 35, "lon": 78, "alt": 50}


class CoordinateConverter:
    """WGS84 converter between geodetic (lat/lon/alt) and local ENU coordinates."""

    def __init__(self, reference_origin: Optional[Dict[str, float]] = None):
        if not reference_origin:
            reference_origin = ORIGIN_LAT_LON
        self.origin = reference_origin

        pipeline = (
            f"+proj=pipeline "
            f"+step +proj=unitconvert +xy_in=deg +z_in=m +xy_out=rad +z_out=m " # Step 1: Degrees to Radians
            f"+step +proj=cart +ellps=WGS84 "                                   # Step 2: Geographic to Geocentric
            f"+step +proj=topocentric +ellps=WGS84 "                            # Step 3: Geocentric to Topocentric ENU
            f"+lon_0={self.origin['lon']} +lat_0={self.origin['lat']} +h_0={self.origin['alt']}"
        )

        self.transformer = Transformer.from_pipeline(pipeline)


    def update_reference_origin(self, origin: Dict[str, float]) -> Dict[str, float]:
        self.origin = origin
        pipeline = (
            f"+proj=pipeline "
            f"+step +proj=unitconvert +xy_in=deg +z_in=m +xy_out=rad +z_out=m " # Step 1: Degrees to Radians
            f"+step +proj=cart +ellps=WGS84 "                                   # Step 2: Geographic to Geocentric
            f"+step +proj=topocentric +ellps=WGS84 "                            # Step 3: Geocentric to Topocentric ENU
            f"+lon_0={self.origin['lon']} +lat_0={self.origin['lat']} +h_0={self.origin['alt']}"
        )

        self.transformer = Transformer.from_pipeline(pipeline)
        return self.origin


    def get_origin(self) -> Dict[str, float]:
        return self.origin


    def lat_lon_alt_to_local(
        self, lat: float, lon: float, alt: float
    ) -> Tuple[float, float, float]:
        """Convert geodetic coordinate to local ENU tuple (x=east, y=north, z=up)."""
        east, north, up = self.transformer.transform(lon, lat, alt, direction=TransformDirection.FORWARD)
        return (east, north, up)


    def local_to_lat_lon_alt(
        self, x: float, y: float, z: float
    ) -> Tuple[float, float, float]:
        lon, lat, alt = self.transformer.transform(x, y, z, direction=TransformDirection.INVERSE)
        return (lat, lon, alt)
    

if __name__ == '__main__':
    scene = load_scene("/home/everetttucker471/Documents/external_test/aerpaw_sionna/data/scenes/lake-wheeler-scene.xml")
    print("Scene loaded, previewing...")
    scene.preview()
