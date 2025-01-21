# Example workflow integration
class GrantAnalysisWorkflow:
    def __init__(self, db_connection, config):
        self.searcher = KeywordGrantSearcher(db_connection, config['keywords'])
        self.scorer = GrantScorer(config['scoring_criteria'])

    def execute(self):
        # Run the search
        raw_results = self.searcher.execute_search()

        # Score and rank results
        scored_results = self.scorer.score_by_criteria(raw_results)

        # Generate report
        report = GrantAnalysisReport(scored_results, self.config)
        return report.generate()