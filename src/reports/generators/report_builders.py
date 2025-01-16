from src.reports.report_base import BaseReport
from datetime import datetime
from src.reports.data_sources import sql_queries as sql


class SampleReport(BaseReport):
    def __init__(self, start_date, end_date, queries=None):
        super().__init__("sample_report", "sample_template")
        self.start_date = start_date
        self.end_date = end_date
        self.queries = queries or sql

    def fill_report(self, doc):
        # Replace placeholders in paragraphs
        for para in doc.paragraphs:
            content = para.text
            content = content.replace('${report_title}', 'Grantor Summary Report')
            content = content.replace('${start_date}', self.start_date.strftime('%Y-%m-%d'))
            content = content.replace('${end_date}', self.end_date.strftime('%Y-%m-%d'))
            content = content.replace('${generation_date}', datetime.now().strftime('%Y-%m-%d %H:%M'))
            content = content.replace('${total_sales}', f"${self.data['total_sales']:,.2f}")
            content = content.replace('${transaction_count}', str(self.data['transaction_count']))
            content = content.replace('${average_transaction}', f"${self.data['average']:,.2f}")
            content = content.replace('${notes}', 'No anomalies noted in this period.')
            content = content.replace('${preparer}', 'Automated System')
            para.text = content

        # Find position to insert table (after "## Details")
        for i, para in enumerate(doc.paragraphs):
            if "## Details" in para.text:
                # Add table after this paragraph
                table = doc.add_table(rows=1, cols=4)
                table.style = 'Table Grid'

                # Add headers
                headers = table.rows[0].cells
                headers[0].text = 'Date'
                headers[1].text = 'Customer'
                headers[2].text = 'Product'
                headers[3].text = 'Amount'

                # Add data
                for sale in self.data['sales']:
                    row = table.add_row().cells
                    row[0].text = sale['date'].strftime('%Y-%m-%d')
                    row[1].text = sale['customer']
                    row[2].text = sale['product']
                    row[3].text = f"${sale['amount']:,.2f}"
                break

    def gather_data(self):
        self.data['sample_view1'] = self.execute_query(self.queries.view1)
        self.data['sample_view2'] = self.execute_query(self.queries.view2)

    def fill_report(self, doc):
        # Just handle the specific template filling logic
        table = doc.add_table(rows=1, cols=3)
        # ... fill in table ...