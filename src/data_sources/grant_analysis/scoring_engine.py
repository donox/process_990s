# data_sources/grant_analysis/scoring_engine.py
from dataclasses import dataclass, fields
from datetime import datetime
from typing import List, Dict, Optional
from src.db_management.transformers.determine_distances import DetermineDistances
from src.db_management.manage_transactions import DBTransaction
import traceback


@dataclass
class ScoringCriteria:
    semantic_similarity_weight: float = 1.0
    grant_size_weight: float = 1.0
    geographic_weight: float = 1.0
    min_grant_size: float = 10000.0


@dataclass
class ScoredResult:
    ein: Optional[str] = None
    name: Optional[str] = None
    score: Optional[float] = None
    semantic_similarity: Optional[float] = None
    total_relevant_grants: Optional[int] = None
    avg_grant_size: Optional[float] = None
    geographic_coverage: Optional[float] = None
    grant_center: Optional[float] = None
    distance_to_target: Optional[float] = None
    scored_date: Optional[datetime] = None


class GrantScorer:
    def __init__(self, config, criteria: ScoringCriteria):
        self.config = config
        self.mg_trans = DBTransaction(config)
        self.austin_zip = '78701'
        self.criteria = criteria
        self.scored_results = []
        self.insert = """
        INSERT INTO grant_analysis_results (ein, foundation_name, score, semantic_similarity, 
          total_relevant_grants, avg_grant_size, geographic_coverage, grant_center, distance_to_target, scored_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ein) DO UPDATE SET
          foundation_name = EXCLUDED.foundation_name,
          score = EXCLUDED.score,
          semantic_similarity = EXCLUDED.semantic_similarity, 
          total_relevant_grants = EXCLUDED.total_relevant_grants,
          avg_grant_size = EXCLUDED.avg_grant_size,
          geographic_coverage = EXCLUDED.geographic_coverage,
          grant_center = EXCLUDED.grant_center,
          distance_to_target = EXCLUDED.distance_to_target,
          scored_date = EXCLUDED.scored_date;"""

    def get_all_results(self):
        return self.scored_results

    def score_all_filers(self):
        filers = self._get_list_of_eins()
        for ein in filers:
            result = self.score_grants(ein)
            if result and type(result) is not bool:
                self._insert_result(result)
                self.scored_results.append(result)

    def score_grants(self, ein: str) -> ScoredResult:
        try:
            scored_result = ScoredResult()
            scored_result.ein = ein
            scored_result.name = self._get_foundation_name(ein)
            scored_result.scored_date = datetime.now()
            scored_result.semantic_similarity = self._get_semantic_similarity(ein)
            grants = self._total_relevant_grants(ein)
            g0 = grants[0]
            g1 = grants[1]
            if not g1:
                g1 = 0
            scored_result.total_relevant_grants = g0
            scored_result.avg_grant_size = g1
            count, dev, centroid = self._get_geographic_coverage(ein)
            scored_result.total_relevant_grants = count
            scored_result.geographic_coverage = dev
            scored_result.grant_center = centroid
            determine_distances = DetermineDistances(self.config, self.austin_zip)
            if ein == '136155552':
                foo = 3
            result_dictionary = determine_distances.get_distances_to_foundation(ein)
            if result_dictionary and type(result_dictionary) is not bool:
                result_dict = determine_distances.determine_distances_to_target(ein, result_dictionary)
                scored_result.distance_to_target = result_dict['recipients']  # distance to centroid of grants
            else:
                return None
            return scored_result
        except Exception as e:
            print(f"Exception in score_grants{e}\n ein: {ein}, :: {result_dictionary}\n",
                  f"{traceback.format_exc()}")

    def _insert_result(self, result: ScoredResult):
        try:
            field_values = [getattr(result, field.name) for field in fields(ScoredResult)]
            if type(field_values[7]) is tuple:
                if field_values[7][0] is None or field_values[7][1] is None:
                    field_values[7] = None
                else:
                    field_values[
                        7] = f"({field_values[7][0]}, {field_values[7][1]})"  # Must Cast location to a POINT string
            self.mg_trans.execute_independent(self.insert, field_values)
        except Exception as e:
            print(f"Fail inserting into grant_analysis: {e}\n Values: {field_values}")
            return None

    def _get_foundation_name(self, ein):
        try:
            result = self.mg_trans.execute_independent("""
                    SELECT businessnameline1 FROM filer
                    where ein = %s;
                """, (ein,))
            res = result[0][0]
            return res
        except Exception as e:
            print(f"Error getting foundation name: {self.ein} with error: {e}")
            return None

    def _get_list_of_eins(self):
        try:
            result = self.mg_trans.execute_independent("""
                    SELECT ein FROM filer
                    """)
            res = [x[0] for x in result]
            return res
        except Exception as e:
            print(f"Error getting list of eins with error: {e}")
            return None

    def _get_semantic_similarity(self, ein):
        try:
            result = self.mg_trans.execute_independent("""
                SELECT similarity_score FROM grant_semantic_score
                where ein = %s;
            """, (ein,))
            if result:
                return result[0][0]
            else:
                return None
        except Exception as e:
            print(f"Error getting semantic similarity for ein: {self.ein} with error: {e}")
            return None

    def _total_relevant_grants(self, ein):
        try:
            result = self.mg_trans.execute_independent("""
                SELECT count(*), avg(amount) FROM grantsbyfiler
                where ein = %s;
            """, (ein,))
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Error getting grantsbyfiler ein: {self.ein} with error: {e}")
            return None

    def _get_geographic_coverage(self, ein):
        try:
                result = self.mg_trans.execute_independent("""
                        SELECT grant_count, deviation, latitude, longtitude FROM grant_geo_score
                        where ein = %s;
                    """, (ein,))
                if result:
                    gc, std, latitude, longtitude = result[0]
                    if type(gc) is not int:
                        return None, None, None
                    if gc < 3:
                        std = None
                    if gc > 0:
                        centroid = (latitude, longtitude)
                    else:
                        centroid = (None, None)
                    return gc, std, centroid
                else:
                    return None, None, None
        except Exception as e:
            print(f"Error getting semantic similarity for ein: {self.ein} with error: {e}")
            return None
