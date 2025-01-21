# data_sources/grant_analysis/scoring_engine.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class ScoringCriteria:
    keyword_weight: float = 1.0
    grant_size_weight: float = 1.0
    geographic_weight: float = 1.0
    min_grant_size: float = 10000.0


@dataclass
class ScoredResult:
    ein: str
    name: str
    score: float
    matched_keywords: List[str]
    total_relevant_grants: int
    avg_grant_size: float
    geographic_coverage: List[str]
    scored_date: datetime
    run_id: str


class GrantScorer:
    def __init__(self, db_connection, criteria: ScoringCriteria):
        self.conn = db_connection
        self.criteria = criteria

    def score_grants(self, search_results, run_id: str) -> List[ScoredResult]:
        scored_results = []
        # Scoring logic here
        return scored_results

    def save_results(self, scored_results: List[ScoredResult], replace_existing: bool = False):
        """Save scored results to database"""
        with self.conn.cursor() as cur:
            if replace_existing:
                cur.execute("DELETE FROM grant_analysis_results WHERE run_id = %s",
                            (scored_results[0].run_id,))

            # Insert new results
            for result in scored_results:
                cur.execute("""
                    INSERT INTO grant_analysis_results 
                    (ein, name, score, matched_keywords, total_relevant_grants,
                     avg_grant_size, geographic_coverage, scored_date, run_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (result.ein, result.name, result.score, result.matched_keywords,
                      result.total_relevant_grants, result.avg_grant_size,
                      result.geographic_coverage, result.scored_date, result.run_id))

    def get_historical_results(self, run_id: Optional[str] = None) -> List[ScoredResult]:
        """Retrieve previous scoring results"""
        with self.conn.cursor() as cur:
            if run_id:
                cur.execute("SELECT * FROM grant_analysis_results WHERE run_id = %s", (run_id,))
            else:
                cur.execute("SELECT * FROM grant_analysis_results ORDER BY scored_date DESC")
            return [ScoredResult(*row) for row in cur.fetchall()]
