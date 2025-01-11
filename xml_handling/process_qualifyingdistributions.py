import os
from datetime import datetime
import psycopg2
import xml.etree.ElementTree as ET


def handler(conn, return_id, root):
    """
    Handler for processing qualifyingdistributions data.
    Extracts data from the XML and inserts it into the `qualifyingdistributions` table.

    Args:
        conn: psycopg2 connection object.
        return_id: The ID of the `returns` table entry.
        root: The XML root element.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Extract qualifyingdistributions data
        qualifyingdistributions = extract_qualifyingdistributions(root)
        if not qualifyingdistributions:
            return True  # No data to process

        # Insert financials data
        insert_qualifyingdistributions(conn, return_id, qualifyingdistributions)
        return True

    except Exception as e:
        print(f"Error processing financials for return ID {return_id}: {e}")
        return False


def extract_qualifyingdistributions(root):
    """
    Extract data for the `financials` table from the XML file.
    """
    financials = root.find('./ReturnData/IRS990PF')
    if financials is None:
        return None

    expenses_contributions = financials.findtext('./PFQualifyingDistributionsGrp/ExpensesAndContributionsAmt', default="0")
    qualifying_distributions = financials.findtext('./PFQualifyingDistributionsGrp/QualifyingDistributionsAmt', default="0")

    return {
        'expenses_contributions': int(float(expenses_contributions)) if expenses_contributions else 0,
        'qualifying_distributions': int(float(qualifying_distributions)) if qualifying_distributions else 0
    }


def insert_qualifyingdistributions(conn, return_id, data):
    """
    Insert data into the `financials` table.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO qualifyingdistributions (returnid, expensesandcontributions, qualifyingdistributions)
                VALUES (%s, %s, %s);
            """, (return_id, data['expenses_contributions'], data['qualifying_distributions']))
    except Exception as e:
        print(f"Error on insert to qualifyingdistributions: {e}")

