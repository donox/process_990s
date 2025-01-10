from db_management.insert_data import load_config, connect_to_db
from db_management.initialize_tables import initialize_tables
from xml_handling.xml_processor import process_directory
import os

PROJECT_BASE = "/home/don/PycharmProjects/Postgres_Chat"
CONFIG_FILE = os.path.join(PROJECT_BASE, "config.yml")
DDL_DIR = os.path.join(PROJECT_BASE, "src/ddl")
xml_dir = '/home/don/Documents/Temp/dev990/summary/20038'


def main():
    # Load configuration
    config = load_config(CONFIG_FILE)

    # Connect to the database
    conn = connect_to_db(config)

    try:
        # Initialize or modify tables
        print("Initializing or modifying database tables...")
        initialize_tables(conn, DDL_DIR)
        process_directory(xml_dir, conn)

        # Additional logic for processing XML files, etc.
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
