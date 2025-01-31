import datetime

from db_management.manage_config import load_config, connect_to_db
from db_management.initialize_tables import initialize_tables, create_zip_coordinates_table, load_zip_data
from xml_handling.xml_processor import process_directory
from reports.generators import single_filer as sf
from reports.generators import list_candidates as lc
from spreadsheets.generators import list_candidates_spreadsheet as lcs
from data_sources.grant_analysis.grant_distribution_analysis import BaseGrantDistributionAnalyzer
from data_sources.grant_analysis.semantic_matching_analysis import SemanticMatching
from db_management.transformers.determine_distances import DetermineDistances
from data_sources.grant_analysis.scoring_engine import GrantScorer, ScoringCriteria
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
zip_code_list = '/home/don/Documents/Wonders/dev990/zip_code_database.csv'

# In-memory list of known unhandled elements
# An unhandled element is a xml element (xpath) that is not processed by the system
# It consists of the element name as appears in the xml and a file where it was encountered.
# It is intended to provide some insight into elements that might be useful and considered for
# adding to the DDL.
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
    setup = False           # Build database and process xml files.
    geo = False             # Analyze locations of foundations, and grants
    keys = False            # Analyze locations of key staff
    semantic = False        # Determine semantic similarity for foundations to WW
    score = False           # Build dict summarizing scoring for a specific ein
    score_all = False       # Determine score for all foundations
    reports = False         # Create reports in docx format
    spreadsheets = True     # Create spreadsheets in xls or csv format
    try:
        if setup:
            # WORK ON DB
            # Initialize or modify tables
            print("Initializing or modifying database tables...")
            # initialize_tables(conn, DDL_DIR)    # Fails on any table modification

            # create and load zip-code table.  Drop existing table before running.
            # create_zip_coordinates_table(conn)
            # load_zip_data(conn, zip_code_list)

            process_directory(xml_dir, conn)
        if geo:
            geo_processor = BaseGrantDistributionAnalyzer(conn)
            geo_processor.execute_analysis()

        if keys:
            key_processor = BaseGrantDistributionAnalyzer(conn)
            key_processor.execute_key_analysis()

        if semantic:
            semantic_processor = SemanticMatching(conn)
            semantic_processor.execute_semantic_analysis()

        if score:
            austin_zip = '78701'
            ein = '010277832'
            determine_distances = DetermineDistances(conn, austin_zip)
            result_dictionary = determine_distances.get_distances_to_foundation(ein)
            result_dict = determine_distances.determine_distances_to_target(ein, result_dictionary)
            result = SemanticMatching.determine_similarity(conn, ein)
            result_dict['similarity'] = result

        if score_all:
            criteria = ScoringCriteria()
            scorer = GrantScorer(conn, criteria)
            scorer.score_all_filers()
            results = scorer.get_all_results()

        if reports:
            # BUILD REPORTS
            # Possible reports:  ['single_filer', 'foundation_list']
            reports_to_build = ['foundation_list']   # List of reports to be generated in this run
            filer_ein = 274133050  # Gallogly Foundation            # ein of filer for filer specific reports
            start_date = str(datetime.date(2023, 1, 1))
            end_date = str(datetime.date(2024, 5, 1))
            other_data = {"start_date": start_date,
                          "end_date": end_date,
                          "filters": {'SelectCandidates': "order by g.distance_to_target asc limit 100;",
                                      },
                          }
            if 'single_filer' in reports_to_build:
                queries = ["FilerSummary", "Contacts", "Grants"]
                params = {"Contacts": (str(filer_ein)),
                          "Grants": (str(filer_ein)),
                          "FilerSummary": str(filer_ein)}
                spreadsheet = sf.SingleFiler(reports_dir, "generated_report", "filer_report",
                                        queries=queries, params=params, other_data=other_data)
                result = spreadsheet.generate()
                print(f"REPORT single_filer: {result}, Done")
            if 'foundation_list' in reports_to_build:
                queries = ['SelectCandidates']
                params = {"Contacts": (str(filer_ein)),
                          "Grants": (str(filer_ein)),
                          "FilerSummary": str(filer_ein)}
                spreadsheet = lc.ListCandidates(reports_dir, "generated_report", "candidate_list",
                                           queries=queries, params=params, other_data=other_data)
                result = spreadsheet.generate()
                print(f"REPORT candidates_list: {result}, Done")

        if spreadsheets:
            spreadsheets_to_build = ['foundation_list']
            start_date = str(datetime.date(2023, 1, 1))
            end_date = str(datetime.date(2024, 5, 1))
            other_data = {"start_date": start_date,
                          "end_date": end_date,
                          "filters": {'SelectCandidates': "order by g.distance_to_target asc limit 100;",
                                      },
                          }
            if 'foundation_list' in spreadsheets_to_build:
                queries = ['SelectCandidates']
                params = {}
                spreadsheet = lcs.ListCandidatesSpreadsheet(reports_dir, "generated_report",
                                           queries=queries, query_params=params, other_data=other_data)
                result = spreadsheet.generate(output_format="xlsx")
                print(f"SPREADSHHET candidates_list: {result}, Done")

        # Additional logic for processing XML files, etc.
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
