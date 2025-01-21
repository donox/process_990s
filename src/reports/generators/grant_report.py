# reports/generators/grant_report.py
class GrantAnalysisReport(report_base.ReportBase):
    def __init__(self, search_results, report_config):
        super().__init__(report_config)
        self.search_results = search_results
        self.transformer = GrantAnalysisTransformer(search_results)

    def prepare_data(self):
        # Transform search results into your standard report format
        self.report_data = self.transformer.transform()

    def generate(self):
        # Use your existing report generation infrastructure
        self.prepare_data()
        return super().generate()