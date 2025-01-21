# data_sources/grant_analysis/geo_utils.py
from typing import List, Tuple, Optional
from math import radians, sin, cos, sqrt, atan2
from statistics import mean, stdev


class ZipDistance:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.known_coordinates = {}  # Memoize data to minimize queries

    def get_zip_coordinates(self, zipcode: str) -> Tuple[float, float]:
        """Get lat/long for a zipcode from database"""
        try:
            result = self.known_coordinates[zipcode]
            return result
        except KeyError:
            pass
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT latitude, longitude 
                FROM zip_coordinates 
                WHERE zipcode = %s
            """, (zipcode,))
            result = cur.fetchone()
            self.known_coordinates[zipcode] = result
            return result if result else None

    def calculate_distance(self, zip1: str, zip2: str) -> float:
        """Calculate distance in miles between two zipcodes"""
        coord1 = self.get_zip_coordinates(zip1)
        coord2 = self.get_zip_coordinates(zip2)
        if not coord1 or not coord2:
            return None

        return self.calculate_coordinate_distance(coord1, coord2)


    @staticmethod
    def calculate_coordinate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance in miles between two coordinate pairs"""
        lat1, lon1 = map(radians, coord1)
        lat2, lon2 = map(radians, coord2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return 3959 * c  # Earth radius in miles


    def find_mean(self, zipcodes: List[str]) -> Tuple[Optional[Tuple[float, float]], Optional[float]]:
        """
        Calculate mean lat/long and standard deviation of distances from mean for a list of zipcodes

        Returns:
            Tuple of (mean_coordinates, standard_deviation)
            For single valid zip, returns (coordinates, None)
            For invalid zips or empty list, returns (None, None)
        """
        coords = []
        for zip_code in zipcodes:
            coord = self.get_zip_coordinates(zip_code)
            if coord:
                coords.append(coord)

        if not coords:
            return (None, None), None

        if len(coords) == 1:
            return coords[0], None

        mean_lat = sum(c[0] for c in coords) / len(coords)
        mean_lon = sum(c[1] for c in coords) / len(coords)
        mean_coord = (mean_lat, mean_lon)

        distances = []
        for coord in coords:
            distance = self.calculate_coordinate_distance(coord, mean_coord)
            distances.append(distance)

        return mean_coord, stdev(distances)
