import os
import yaml
import logging
import pandas as pd
import xlsxwriter
import psycopg2
from datetime import datetime
from pathlib import Path
from src.data_sources.queries import QUERIES
from src.reports.report_base import BaseReport  # Reusing query execution logic


class BaseSpreadsheet:
    def __init__(self, report_name, queries, query_params):
        """
        Args:
            report_name: name of the spreadsheet report
            queries: list of query names to execute
            query_params: dict mapping query names to their parameters
        """
        self.report_name = report_name
        self.queries_to_run = queries
        self.query_params = query_params
        self.queries = QUERIES
        self.logger = None
        self.config = self._load_config()
        self.setup_logging()
        self.db_conn = None
        self.data = None
        self.dataframes = None

    @staticmethod
    def _load_config():
        base_dir = Path(__file__).parent.parent
        base_dir = base_dir.parent       # config file is stored with project
        config_path = os.path.join(base_dir, 'config.yml')   # config file is stored with project
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def setup_logging(self):
        self.logger = logging.getLogger(self.report_name)
        # Add logging setup here

    def get_db_connection(self):
        if not self.db_conn:
            db_config = self.config['database']
            try:
                self.db_conn = psycopg2.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    dbname=db_config['database'],
                    user=db_config['username'],
                    password=db_config['password']
                )
            except Exception as e:
                self.logger.error(f"Database connection failed: {e}")
                raise
        return self.db_conn

    def execute_query(self, query_list, filters=None):
        """Execute the named queries

        Args:
            query_list: list of query names to execute
            filter: a dictionary of sql expressions to add to a query before executing
                    keys are the names of the query to be filtered
        Returns:
            Dict mapping query names to their results
        """
        results = {}
        columns = {}
        conn = self.get_db_connection()

        try:
            with conn.cursor() as cur:
                for query_name in query_list:
                    # Get the actual SQL from our collected queries
                    sql = self.queries[query_name].rstrip()
                    if filters and query_name in filters.keys():
                        if sql.endswith('**FILTER**;'):
                            sql = sql.replace('**FILTER**;', filters[query_name])
                    elif not filters:
                        sql.replace('**FILTER**;', ';')
                    else:
                        raise ValueError(f"Query {query_name} does not support filter, but one given")
                    sql = sql.lower()
                    if query_name in self.query_params.keys():
                        params = self.query_params[query_name]
                        if type(params) not in (list, tuple):
                            params = (params,)
                        cur.execute(sql, params)     # parameter must be tuple or list
                    else:
                        cur.execute(sql)
                    results[query_name] = cur.fetchall()
                    columns[query_name] = [desc[0] for desc in cur.description]
            self.data = results
            self.dataframes = {query: pd.DataFrame(result, columns=columns[query]) for
                               query, result in self.data.items()}
            return results

        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            conn.rollback()
            raise
    # def execute_query(self):
    #     """Execute queries and store results in a Pandas DataFrame"""
    #     report = BaseReport(self.report_name, None, self.queries_to_run, self.query_params)
    #     self.data = self.execute_query(self.queries_to_run)
    #     self.dataframes = {query: pd.DataFrame(result) for query, result in self.data.items()}

    def generate(self):
        """Main execution method"""
        self.logger.info(f"Starting report generation: {self.report_name}")
        start_time = datetime.now()

        try:
            self.gather_data()
            doc = self.get_template()
            self.fill_report(doc)
            self.save_report(doc)

            duration = datetime.now() - start_time
            self.logger.info(f"Report completed in {duration}")

        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise
        finally:
            self.cleanup()

    # Methods to be implemented by specific reports
    def gather_data(self):
        """Override to gather needed data"""
        raise NotImplementedError

    def fill_report(self, doc):
        """Override to fill the template"""
        raise NotImplementedError

    def _get_archive_path(self, file_name, file_type):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        fn = f'{file_name}_{timestamp}'
        archive_dir = os.path.join(
            self.config['paths']['output_dir'],
            datetime.now().strftime('%Y-%m')
        )
        archive_dir = os.path.join(self.reports_dir, archive_dir)
        os.makedirs(archive_dir, exist_ok=True)

        full_path = os.path.join(archive_dir, f"{fn}.{file_type}")
        return full_path

    def _get_current_path(self, file_name, file_type):
        current_path = os.path.join(
            self.config['paths']['output_dir'],
            'current',
            f"{file_name}_latest.{file_type}"
        )
        current_path = os.path.join(self.reports_dir, current_path)
        return current_path

    def save_to_csv(self, output_dir="output"):
        """Save DataFrames to CSV files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        os.makedirs(output_dir, exist_ok=True)

        for query_name, df in self.dataframes.items():
            fn = f"{self.report_name}_{query_name}".lower()
            archive_path = self._get_archive_path(fn, 'csv')
            df.to_csv(archive_path, index=False)
            current_path = self._get_current_path(fn, 'csv')
            df.to_csv(current_path, index=False)
            print(f"Saved CSV: {current_path}")

    def save_to_excel(self, output_dir="output"):
        """Save DataFrames to an Excel file with multiple sheets"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        os.makedirs(output_dir, exist_ok=True)

        for query_name, df in self.dataframes.items():
            fn = f"{self.report_name}_{query_name}".lower()
            archive_path = self._get_archive_path(fn, 'xlsx')
            with pd.ExcelWriter(archive_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name=query_name, index=False)
            current_path = self._get_current_path(fn, 'xlsx')
            with pd.ExcelWriter(current_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name=query_name, index=False)

        print(f"Saved Excel: {current_path}")
