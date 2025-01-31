from src.spreadsheets.spreadsheet_base import BaseSpreadsheet


class GrantSpreadsheet(BaseSpreadsheet):
    def __init__(self, report_name, queries, query_params, other_data=None):
        self.other_data = other_data
        super().__init__(report_name, queries, query_params)

    def gather_data(self):
        # Need to pass filters which should be an entry in other_data whose value is a dictionary of filters
        if self.other_data and 'filters' in self.other_data.keys():
            self.data = self.execute_query(self.queries_to_run, filters=self.other_data['filters'])
        else:
            self.data = self.execute_query(self.queries_to_run)
        # self.data is a dictionary with entry key of query_name whose value is the result of running the query.
        # self.dataframes contains the result of the queries.

    def generate(self, output_format="csv"):
        """Run queries and export results in the desired format"""
        self.gather_data()

        if output_format == "csv":
            self.save_to_csv()
        elif output_format == "xlsx":
            self.save_to_excel()
        else:
            raise ValueError("Unsupported format: Choose 'csv' or 'xlsx'")
