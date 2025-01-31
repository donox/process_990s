from src.spreadsheets.spreadsheet_base import BaseSpreadsheet
from src.data_sources.queries import sql_queries as sql
import traceback


class ListCandidatesSpreadsheet(BaseSpreadsheet):
    def __init__(self, reports_dir, report_name, queries=None, query_params=None, other_data=None):
        self.queries = queries or sql
        self.reports_dir = reports_dir
        self.other_data = other_data
        super().__init__(report_name, queries, query_params)

    def generate(self, output_format="csv"):
        """Run queries and export results in the desired format"""
        # Need to pass filters which should be an entry in other_data whose value is a dictionary of filters
        if self.other_data and 'filters' in self.other_data.keys():
            self.data = self.execute_query(self.queries_to_run, filters=self.other_data['filters'])
        else:
            self.data = self.execute_query(self.queries_to_run)
        # self.data is a dictionary with entry key of query_name whose value is the result of running the query.

        if output_format == "csv":
            self.save_to_csv(output_dir=self.reports_dir)
        elif output_format == "xlsx":
            self.save_to_excel(output_dir=self.reports_dir)
        else:
            raise ValueError("Unsupported format: Choose 'csv' or 'xlsx'")
