import yaml
import logging
from datetime import datetime
import os
import psycopg2
from docx import Document
from pathlib import Path
from src.data_sources.queries import QUERIES


class BaseReport:
    def __init__(self, report_name, template_name, queries, query_params):
        """
        Args:
            report_name: name of the report
            template_name: name of template file
            queries: list of query names to execute
            query_params: dict mapping query names to their parameters
        """
        self.report_name = report_name
        self.template_name = template_name
        self.queries_to_run = queries
        self.query_params = query_params
        self.queries = QUERIES
        self.config = self._load_config()
        self.setup_logging()
        self.db_conn = None
        self.data = {}

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

    def check_database(self):
        return
        conn = self.get_db_connection()

        try:
            with conn.cursor() as cur:
                # Check which database we're connected to
                cur.execute("SELECT current_database();")
                db = cur.fetchone()[0]
                print(f"Connected to database: {db}")

                # List ALL tables in ALL schemas
                cur.execute("""
                    SELECT schemaname, tablename 
                    FROM pg_tables 
                    WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
                """)
                tables = cur.fetchall()
                print(f"All available tables: {tables}")

                # Check schemas
                cur.execute("""
                    SELECT nspname 
                    FROM pg_namespace 
                    WHERE nspname NOT IN ('pg_catalog', 'information_schema');
                """)
                schemas = cur.fetchall()
                print(f"Available schemas: {schemas}")

        except Exception as e:
            print(f"Error checking database: {e}")
            conn.rollback()
            raise

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

            return results

        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            conn.rollback()
            raise

    def gather_data(self):
        # Single query      # overridden in initiating report builder
        raise NotImplementedError
        # self.data.update(self.execute_query('sales', (self.start_date, self.end_date)))
        #
        # # Multiple queries with same parameters
        # self.data.update(self.execute_query(
        #     ['sales', 'customers'],
        #     (self.start_date, self.end_date)
        # ))
        #
        # # Multiple queries with different parameters
        # self.data.update(self.execute_query(
        #     ['sales', 'inventory'],
        #     {
        #         'sales': (self.start_date, self.end_date),
        #         'inventory': (self.warehouse_id,)
        #     }
        # ))

    def get_template(self):
        """Load the document template and return Document object"""
        relative_path = os.path.join(
            self.config['paths']['templates'],
            f"{self.template_name}.docx"
        )
        template_path = os.path.join(self.reports_dir, relative_path)

        try:
            doc = Document(template_path)
            return doc
        except Exception as e:
            self.logger.error(f"Template load failed: {e}")
            raise

    def save_report(self, doc):
        """Save with standardized naming and path"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{self.report_name}_{timestamp}.docx"

        # Create dated archive directory if needed
        archive_dir = os.path.join(
            self.config['paths']['output_dir'],
            datetime.now().strftime('%Y-%m')
        )
        archive_dir = os.path.join(self.reports_dir, archive_dir)
        os.makedirs(archive_dir, exist_ok=True)

        full_path = os.path.join(archive_dir, filename)
        try:
            doc.save(full_path)
            self.logger.info(f"Report saved: {full_path}")

            # Also save to 'current' folder
            current_path = os.path.join(
                self.config['paths']['output_dir'],
                'current',
                f"{self.report_name}_latest.docx"
            )
            current_path = os.path.join(self.reports_dir, current_path)
            doc.save(current_path)
        except Exception as e:
            self.logger.error(f"Save failed: {e}")
            raise

    def cleanup(self):
        """Clean up resources"""
        if self.db_conn:
            self.db_conn.close()

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
