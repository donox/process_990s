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
