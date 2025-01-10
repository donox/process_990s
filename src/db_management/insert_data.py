import yaml
import psycopg2
from psycopg2 import sql


def load_config(config_path):
    """
    Load configuration from a YAML file.
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def connect_to_db(config):
    """
    Establish a connection to the PostgreSQL database.
    """
    db_config = config['database']
    conn = psycopg2.connect(
        host=db_config['host'],
        port=db_config['port'],
        dbname=db_config['database'],
        user=db_config['username'],
        password=db_config['password']
    )
    return conn


def initialize_tables(conn, ddl_file):
    """
    Create tables using the provided DDL file.
    """
    with conn.cursor() as cur:
        with open(ddl_file, 'r') as ddl:
            cur.execute(ddl.read())
        conn.commit()


def insert_data(conn, data):
    """
    Insert parsed XML data into the database.
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO returns (return_id, tax_year, return_type, tax_period_start, tax_period_end)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (data['return_id'], data['tax_year'], data['return_type'], data['tax_period_start'], data['tax_period_end']))
        return_id = cur.fetchone()[0]

        # Insert related data (filer, financials, etc.)
        # Example for filer
        cur.execute("""
            INSERT INTO filer (return_id, ein, business_name_line1, business_name_line2, phone_number,
                               address_line1, city, state, zip)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (return_id, data['filer']['ein'], data['filer']['business_name_line1'],
              data['filer']['business_name_line2'], data['filer']['phone_number'],
              data['filer']['address_line1'], data['filer']['city'],
              data['filer']['state'], data['filer']['zip']))

        conn.commit()
