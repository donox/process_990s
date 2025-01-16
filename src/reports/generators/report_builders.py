from src.reports.report_base import BaseReport
from datetime import datetime
from src.reports.data_sources.queries import sql_queries as sql


class SampleReport(BaseReport):
    """
     Args:
         report_name: name of the report
         template_name: name of template file
         queries: list of query names to execute
         query_params: dict mapping query names to their parameters
     """
    # rb.SampleReport(datetime.date(2001, 1, 1), datetime.date(2022, 2, 2), "sample_report", queries=["View1", "View2"])
    #
    def __init__(self, reports_dir, report_name, report_template, queries=None, params=None):
        self.queries = queries or sql
        self.reports_dir = reports_dir
        super().__init__(report_name, report_template, self.queries, params)

    def fill_report(self, doc):

        replacements = {
            '${report_title}': 'Grantor Summary Report',
            '${generation_date}': datetime.now().strftime('%Y-%m-%d %H:%M'),
            '${preparer}': 'Automated System',
        }
        # Replace placeholders in paragraphs
        for para in doc.paragraphs:
            content = para.text
            # Only process paragraphs that contain at least one placeholder
            if '${' in content:
                for key, value in replacements.items():
                    if key in content:
                        content = content.replace(key, value)
                para.text = content

        # Find position to insert table (after "## Details")
        for i, para in enumerate(doc.paragraphs):
            if "[Details]" in para.text:
                para.text = ""    # remove commentary on table insertion
                # Add table after this paragraph
                table = doc.add_table(rows=1, cols=4)
                # table.style = 'Table Grid'

                # Add headers
                headers = table.rows[0].cells
                headers[0].text = 'Foundation'
                headers[1].text = 'City'
                headers[2].text = 'Amount'
                headers[3].text = 'Purpose'

                # Add data
                for grant in self.data['View1']:
                    print(f"tuple count: {len(grant)}")
                    row = table.add_row().cells
                    row[0].text = grant[0]
                    row[1].text = grant[3]
                    row[2].text = f"${grant[7]:,.2f}"
                    row[3].text = grant[6]
                break

    def gather_data(self):
        self.data = self.execute_query(self.queries_to_run)


