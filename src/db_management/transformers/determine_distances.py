from src.data_sources.grant_analysis.geo_utils import ZipDistance
import traceback


class DetermineDistances():
    """Class to make distance calculations from source to target foundations."""
    def __init__(self, db_connection, target_zipcode):
        self.conn = db_connection
        self.zip_distance = ZipDistance(db_connection)
        self.target = target_zipcode
        self.target_coordinates = self.zip_distance.get_zip_coordinates(target_zipcode.lstrip('0'))
        self.filer_zip_coord_query = """
            select ein, zipcode from filer 
                where ein = %s;
        """
        self.distances_query = """
            select f.ein, f,zipcode, ggs.grant_count as grant_count, ggs.longtitude as grant_longitude,
                ggs.latitude  as grant_latitude, ggs.deviation as grant_deviation,
                ggs.filer_to_centroid as grant_to_filer,
                ggs.key_longtitude as key_longitude, ggs.key_latitude as key_latitude,
                ggs.filer_to_key_centroid as key_to_filer, ggs.key_count as key_count
                from filer f
                join grant_geo_score ggs
                on f.ein = ggs.ein
                where f.ein = %s
                ;"""
        self.distance_names = ['ein', 'foundation_address', 'foundation_zip', 'grant_count', 'grant_longitude',
                               'grant_latitude',
                               'grant_deviation', 'grant_to_filer', 'key_longitude', 'key_latitude', 'key_to_filer',
                               'key_count']

    def get_distances_to_foundation(self, ein):
        foundation_zip = None
        try:
            with self.conn.cursor() as cur:
                cur.execute(self.filer_zip_coord_query, (ein,))
                foundation_zip = cur.fetchone()[1]
        except Exception as e:
            print(f"Failure retrieving foundation {ein} zipcode\n  {traceback.format_exc()}")
            return None
        if not foundation_zip:
            print(f"Foundation Zip not found in query")
            return None
        foundation_zip = foundation_zip.lstrip('0')
        foundation_coordinates = self.zip_distance.get_zip_coordinates(foundation_zip)
        if not foundation_coordinates:
            return None
        results = None
        try:
            with self.conn.cursor() as cur:
                cur.execute(self.distances_query, (ein,))
                results = cur.fetchall()
        except Exception as e:
            print(f"Foundation geo data fail: {e}")
            return None
        if not results:
            return None
        result_dict = {'foundation_longitude': foundation_coordinates[1],
                       'foundation_latitude': foundation_coordinates[0]
                       }
        for name, value in zip(self.distance_names, results[0]):
            result_dict[name] = value
        return result_dict

    def determine_distances_to_target(self, ein, result_dict):
        try:
            foundation_coord = (result_dict['foundation_latitude'], result_dict['foundation_longitude'])
            key_staff_coord = (result_dict['key_latitude'], result_dict['key_longitude'])
            recipients_coord = (result_dict['grant_latitude'], result_dict['grant_longitude'])
            dist_to_foundation = dist_to_key_staff = dist_to_recipients = None
            if foundation_coord[0]:
                dist_to_foundation = self.zip_distance.calculate_coordinate_distance(self.target_coordinates,
                                                                                     foundation_coord)
            if key_staff_coord[0]:
                dist_to_key_staff = self.zip_distance.calculate_coordinate_distance(self.target_coordinates,
                                                                                     key_staff_coord)
            if recipients_coord[0]:
                dist_to_recipients = self.zip_distance.calculate_coordinate_distance(self.target_coordinates,
                                                                                     recipients_coord)
            result = {'foundation': dist_to_foundation,
                      "key_contacts": dist_to_key_staff,
                      "recipients": dist_to_recipients}
            return result
        except Exception as e:
            print(f"Fail in distance to target: {2}\n  {traceback.format_exc()}")
            return None


