import datetime

from db_management.insert_data import load_config, connect_to_db
from db_management.initialize_tables import initialize_tables
from xml_handling.xml_processor import process_directory
from reports.generators import report_builders as rb
import os
import csv

PROJECT_BASE = "/home/don/PycharmProjects/Postgres_Chat"
CONFIG_FILE = os.path.join(PROJECT_BASE, "config.yml")
UNHANDLED = os.path.join(PROJECT_BASE, "unhandled_elements.csv")
DDL_DIR = os.path.join(PROJECT_BASE, "src/ddl")
xml_dir = '/home/don/Documents/Wonders/dev990'
reports_dir = '/home/don/Documents/Wonders/reports'
include_dirs = ['2023', '2024']
exclude_dirs = ['zip_files', 'raw', 'result', 'summary', 'data', 'logs']

# In-memory list of known elements
known_elements = []


def load_unhandled():
    """
    Load elements from the 'UNHANDLED' file into the in-memory list.
    """
    if os.path.exists(UNHANDLED):
        with open(UNHANDLED, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            global known_elements
            known_elements = [row[0] for row in reader]


def add_unhandled(file_path, element):
    """
    Add an element to the UNHANDLED CSV file and in-memory list if it's not already present.

    Args:
        file_path (str): The file path to the UNHANDLED CSV.
        element (str): The new element to check and possibly add.
    """
    global known_elements

    if element not in known_elements:
        # Add to in-memory list
        known_elements.append(element)
        # Append to the CSV file
        with open(UNHANDLED, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([element, file_path])


def main():
    # Load configuration
    config = load_config(CONFIG_FILE)

    # Load known elements from the 'UNHANDLED' file
    load_unhandled()

    # Connect to the database
    conn = connect_to_db(config)

    try:
        # WORK ON DB
        # Initialize or modify tables
        # print("Initializing or modifying database tables...")
        # initialize_tables(conn, DDL_DIR)    # Fails on any table modification
        # process_directory(xml_dir, conn)

        # BUILD REPORTS
        start_date = datetime.date(2001, 1,1)
        end_date = datetime.date(2002, 1, 1)
        queries = ["View1", "View2"]
        params = {"View1": (start_date, end_date)}
        report = rb.SampleReport(reports_dir,"generated_report", "sample_report",
                                 queries=queries, params=params)
        result = report.generate()
        print(f"REPORT: {result}, Done")

        # Additional logic for processing XML files, etc.
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
