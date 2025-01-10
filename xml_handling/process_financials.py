import os
from datetime import datetime
import psycopg2
import xml.etree.ElementTree as ET


def handler(conn, return_id, root):
    """
    Handler for processing financials data.
    Extracts data from the XML and inserts it into the `financials` table.

    Args:
        conn: psycopg2 connection object.
        return_id: The ID of the `returns` table entry.
        root: The XML root element.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Extract financials data
        financials = extract_financials(root)
        if not financials:
            return True  # No data to process

        # Insert financials data
        insert_financials(conn, return_id, financials)
        return True

    except Exception as e:
        print(f"Error processing financials for return ID {return_id}: {e}")
        return False


def extract_financials(root):
    """
    Extract data for the `financials` table from the XML file.
    """
    financials = root.find('./ReturnData/IRS990PF')
    if financials is None:
        return None

    fmv_assets_eoy = financials.findtext('./FMVAssetsEOYAmt', default="0")
    qualifying_distributions = financials.findtext('./PFQualifyingDistributionsGrp/QualifyingDistributionsAmt', default="0")

    return {
        'fmv_assets_eoy': int(float(fmv_assets_eoy)) if fmv_assets_eoy else 0,
        'qualifying_distributions': int(float(qualifying_distributions)) if qualifying_distributions else 0
    }


def insert_financials(conn, return_id, data):
    """
    Insert data into the `financials` table.
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO financials (return_id, fmv_assets_eoy, qualifying_distributions)
            VALUES (%s, %s, %s);
        """, (return_id, data['fmv_assets_eoy'], data['qualifying_distributions']))
