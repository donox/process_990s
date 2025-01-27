from src.reports.report_base import BaseReport
from datetime import datetime
from src.data_sources.queries import sql_queries as sql
import traceback


class ListCandidates(BaseReport):
    """
     Args:
         reports_dir: file system directory for managing reports
         report_name: name of the report
         template_name: name of template file
         queries: list of query names to execute
         query_params: dict mapping query names to their parameters
         other_data: dict of data directly for the report writer
     """

    def __init__(self, reports_dir, report_name, report_template, queries=None, params=None, other_data=None):
        self.queries = queries or sql
        self.reports_dir = reports_dir
        self.other_data = other_data
        super().__init__(report_name, report_template, self.queries, params)

    def gather_data(self):
        # Need to pass filters which should be an entry in other_data whose value is a dictionary of filters
        if self.other_data and 'filters' in self.other_data.keys():
            self.data = self.execute_query(self.queries_to_run, filters=self.other_data['filters'])
        else:
            self.data = self.execute_query(self.queries_to_run)
        # self.data is a dictionary with entry key of query_name whose value is the result of running the query.

    def fill_report(self, doc):
        emu = 914400  # 1 in. in English Metric Units (EMU)
        replacements = {
            '${report_title}': '100 Closest Foundations ',
            '${generation_date}': datetime.now().strftime('%Y-%m-%d %H:%M'),
            '${preparer}': 'Don Oxley',
        }
        self._extract_query_summary(replacements)

        for i, para in enumerate(doc.paragraphs):
            content = para.text
            # Only process paragraphs that contain at least one placeholder
            if '${' in content:
                for key, value in replacements.items():
                    if key in content:
                        content = content.replace(key, value)
                para.text = content

            # Find position to insert table (after "[Candidates]")
            elif "[Candidates]" in para.text:
                para.text = ""  # remove commentary on table insertion
                # Add table after this paragraph
                table = doc.add_table(rows=1, cols=6)
                # Insert table after current paragraph
                para._p.addnext(table._tbl)
                widths = [4 * emu, int(.4 * emu), int(.8 * emu), int(.8 * emu), int(.6 * emu)]
                for idx, width in enumerate(widths):
                    table.columns[idx].width = width
                # table.style = 'Table Grid'            # No settable styles - use defaults

                # Add headers in bold
                headers = table.rows[0].cells
                header_texts = ['Name', 'St', 'Grants', '$$', 'Like', 'Miles']
                for idx, text in enumerate(header_texts):
                    cell = headers[idx]
                    paragraph = cell.paragraphs[0]
                    run = paragraph.add_run(text)
                    run.bold = True

                # Add data
                try:
                    for candidate in self.data['SelectCandidates']:
                        row = table.add_row().cells
                        row[0].text = candidate[4]        # Name
                        row[1].text = candidate[0]        # State
                        row[2].text = str(candidate[7])        # Number grants
                        txt = str(candidate[8])            # pick off dollars only
                        ndx = txt.find('.')
                        row[3].text = txt[:ndx] if ndx != -1 else ''      # Grant Size
                        sim = str(candidate[6])
                        row[4].text = '' if sim is None else sim[:4]    # 2 digits of similarity
                        dist = str(candidate[11])
                        ndx = dist.find('.')
                        row[5].text = dist[:ndx] if ndx != -1 else ''   # Take whole miles only
                        foo=3
                except TypeError as e:
                    print(f"Error building rows: {e}, \n {traceback.format_exc()}")
                    foo = 3

    def _extract_query_summary(self, replacements):
        # combine items from other_data into single dictionary (replacements)
        # *** This presumes a single query where the call might actually be a list of queries ***
        for key, value in self.other_data.items():
            if key != 'filters':            # no longer have use for filters
                replacements[f"${{{key}}}"] = value
        # summary contains all data retrieved from 'SelectCandidates'
        # query returns state, zip from filer, all of grant_analysis_results
        summary = self.data["SelectCandidates"]
        elements = (0, 1,  3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        names = ("state",
                 "zipcode",
                 # "id",       # Don't need db index
                 "ein",
                 "foundation_name",
                 "score",
                 "semantic_similarity",
                 "total_relevant_grants",
                 "avg_grant_size",
                 "geographic_coverage",
                 "grant_center",
                 "distance_to_target",
                 "scored_date")
        for index, name in zip(elements, names):
            # build dictionary of columns from query
            replacements[f"${{{name}}}"] = [str(x[index]) for x in summary]
        foo = 3
