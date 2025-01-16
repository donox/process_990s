import yaml
import logging
from datetime import datetime
import os
import psycopg2
from docx import Document


class BaseReport:
    def __init__(self, report_name, template_name):
        self.report_name = report_name
        self.template_name = template_name
        self.config = self._load_config()
        self.setup_logging()
        self.db_conn = None
        self.data = {}  # Store query results

    @staticmethod
    def _load_config(self):
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def setup_logging(self):
        self.logger = logging.getLogger(self.report_name)
        # Add logging setup here

    def get_db_connection(self):
        if not self.db_conn:
            try:
                self.db_conn = psycopg2.connect(**self.config['database'])
            except Exception as e:
                self.logger.error(f"Database connection failed: {e}")
                raise
        return self.db_conn

    def execute_query(self, query_name, params=None):
        """Execute a named query with optional parameters"""
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                cur.execute(self.queries[query_name], params)
                return cur.fetchall()
        except Exception as e:
            self.logger.error(f"Query {query_name} failed: {e}")
            raise

    def get_template(self):
        """Load the document template"""
        template_path = os.path.join(
            self.config['paths']['templates'],
            f"{self.template_name}.docx"
        )
        try:
            return Document(template_path)
        except Exception as e:
            self.logger.error(f"Template load failed: {e}")
            raise

    def save_report(self, doc):
        """Save with standardized naming and path"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{self.report_name}_{timestamp}.docx"

        # Create dated archive directory if needed
        archive_dir = os.path.join(
            self.config['paths']['output'],
            datetime.now().strftime('%Y-%m')
        )
        os.makedirs(archive_dir, exist_ok=True)

        full_path = os.path.join(archive_dir, filename)
        try:
            doc.save(full_path)
            self.logger.info(f"Report saved: {full_path}")

            # Also save to 'current' folder
            current_path = os.path.join(
                self.config['paths']['output'],
                'current',
                f"{self.report_name}_latest.docx"
            )
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
