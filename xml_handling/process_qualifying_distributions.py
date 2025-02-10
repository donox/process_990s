import os
from datetime import datetime
import psycopg2
import xml.etree.ElementTree as ET


def handler(mg_trans, return_id, root, file_path):
    """
    Handler for processing qualifyingdistributions data.
    Extracts data from the XML and inserts it into the `qualifyingdistributions` table.

    Args:
        mg_trans: db connection object.
        return_id: The ID of the `returns` table entry.
        root: The XML root element.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Extract qualifyingdistributions data
        qualifying_distributions = extract_qualifying_distributions(root, file_path)
        if not qualifying_distributions:
            return True  # No data to process

        # Insert financials data
        insert_qualifying_distributions(mg_trans, return_id, qualifying_distributions)
        return True

    except Exception as e:
        print(f"Error processing financials for return ID {return_id}: {e}")
        return False


def extract_qualifying_distributions(root, file_path):
    """
    Extract data for the `financials` table from the XML file.
    """
    financials = root.find('./ReturnData/IRS990PF')
    if financials is None:
        return None

    expenses_contributions = financials.findtext('./PFQualifyingDistributionsGrp/ExpensesAndContributionsAmt',
                                                 default="0")
    qualifying_distributions = financials.findtext('./PFQualifyingDistributionsGrp/QualifyingDistributionsAmt',
                                                   default="0")

    return {
        'expenses_contributions': int(float(expenses_contributions)) if expenses_contributions else 0,
        'qualifying_distributions': int(float(qualifying_distributions)) if qualifying_distributions else 0
    }


def insert_qualifying_distributions(mg_trans, return_id, data):
    """
    Insert data into the `financials` table.
    """
    try:
        query = """
            INSERT INTO qualifyingdistributions (returnid, expensesandcontributions, qualifyingdistributions)
            VALUES (%s, %s, %s)
            ON CONFLICT (returnid) DO UPDATE
            SET expensesandcontributions = EXCLUDED.expensesandcontributions,
                qualifyingdistributions = EXCLUDED.qualifyingdistributions;
            """
        params = (return_id, data['expenses_contributions'], data['qualifying_distributions'])
        result = mg_trans.execute(query, params=params)
        if not result:
            raise ValueError(f"qualifyingdistribution failed.")
    except Exception as e:
        print(f"Error on insert to qualifyingdistribution: {e}")
        raise e
