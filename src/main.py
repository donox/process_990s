import datetime

from db_management.insert_data import load_config, connect_to_db
from db_management.initialize_tables import initialize_tables, create_zip_coordinates_table, load_zip_data
from xml_handling.xml_processor import process_directory
from reports.generators import single_filer as sf
from data_sources.grant_analysis.grant_distribution_analysis import BaseGrantDistributionAnalyzer
from data_sources.grant_analysis.semantic_matching_analysis import SemanticMatching
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
zip_code_list ='/home/don/Documents/Wonders/dev990/zip_code_database.csv'

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
    setup = False
    geo = False
    semantic = True
    reports = False
    try:
        if setup:
            # WORK ON DB
            # Initialize or modify tables
            print("Initializing or modifying database tables...")
            # initialize_tables(conn, DDL_DIR)    # Fails on any table modification

            # create and load zip-code table.  Drop existing table before running.
            # create_zip_coordinates_table(conn)
            # load_zip_data(conn, zip_code_list)

            # process_directory(xml_dir, conn)
        if geo:
            geo_processor = BaseGrantDistributionAnalyzer(conn)
            geo_processor.execute_analysis()

        if semantic:
            semantic_processor = SemanticMatching(conn)
            semantic_processor.execute_semantic_analysis()

        if reports:
            # BUILD REPORTS
            filer_ein = 274133050       # Gallogly Foundation
            start_date = str(datetime.date(2023, 1,1))
            end_date = str(datetime.date(2024, 5, 1))
            queries = ["FilerSummary", "Contacts", "Grants"]
            params = {"Contacts": (str(filer_ein)),
                      "Grants": (str(filer_ein)),
                      "FilerSummary": str(filer_ein)}
            other_data = {"start_date": start_date,
                          "end_date": end_date}
            report = sf.SingleFiler(reports_dir, "generated_report", "filer_report",
                                    queries=queries, params=params, other_data=other_data)
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
