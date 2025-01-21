from src.data_sources.grant_analysis.geo_utils import ZipDistance
from collections import defaultdict
from src.data_sources.queries.geo_queries import GEO_QUERIES
from statistics import mean, stdev
import traceback


class BaseGrantDistributionAnalyzer:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.zip_calcs = ZipDistance(self.conn)
        self.filer_grants = defaultdict(list)
        self.query = GEO_QUERIES['GrantLocations']
        self.insert = """
        INSERT INTO grant_geo_score (EIN, grant_count, longtitude, latitude, deviation, filer_to_centroid)
                VALUES (%s, %s, %s, %s, %s, %s);"""
        try:
            with self.conn.cursor() as cur:
                count = 0
                cur.execute(self.query)
                for row in cur.fetchall():
                    ein = row[0]
                    self.filer_grants[ein].append({
                        'foundation': row[1],
                        'filer_zip': row[2],
                        'grant_zip': row[3],
                        'amount': row[4],
                    })
                    count += 1
                    if count > 10000000:
                        break
        except Exception as e:
            print(f"Geo query failure: {e}")

    def execute_analysis(self):
        # iter_count = 0
        # for ein, grants in self.filer_grants.items():
        #     for grant in grants:
        #         iter_count += 1
        # print(f"Total EIN: {iter_count}")
        # return
        for ein, grants in self.filer_grants.items():
            try:
                # Process filer
                base_zip = None
                grant_count = 0
                grant_locs = []
                for grant in grants:
                    if not base_zip:
                        base_zip = grant['filer_zip']
                        if base_zip:
                            base_zip = base_zip[:5]
                    grant_zip = grant['grant_zip']
                    if grant_zip:
                        grant_zip = grant_zip[:5]
                        grant_locs.append(grant_zip)
                        grant_count += 1
                centroid, deviation = self.zip_calcs.find_mean(grant_locs)
                print(f"Centroid: {centroid}, StDev: {deviation}")

                if centroid[0]:
                    base_coord = self.zip_calcs.get_zip_coordinates(base_zip)
                    if base_coord:
                        filer_to_centroid = self.zip_calcs.calculate_coordinate_distance(base_coord, centroid)
                    else:
                        filer_to_centroid = None
                else:
                    filer_to_centroid = None
                try:
                    with self.conn.cursor() as cur:
                        cur.execute(self.insert, (str(ein), grant_count, centroid[0], centroid[1], deviation,
                                                  filer_to_centroid))
                        self.conn.commit()
                except Exception as e:
                    print(f"Error inserting geo data: {e}")
                    self.conn.rollback()

            except Exception as e:
                print(f"Fail in calculating distance stats: {e}\n {traceback.format_exc()}")
