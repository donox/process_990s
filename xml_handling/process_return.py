import os
from datetime import datetime
import psycopg2
import xml.etree.ElementTree as ET


def extract_returns(root, file_path):
    """
    Extract data for the `returns` table from the XML file.
    """
    return_id = file_path.split('/')[-1].replace('.xml', '')  # Use file name as return ID
    tax_year = root.attrib.get('year', '0')  # Extract the `year` attribute from `<Results>`
    return_type = root.findtext('ReturnTypeCd', default="")  # Correct path for `ReturnTypeCd`

    tax_period_end_raw = root.findtext('TaxPeriodEndDt', default="")
    tax_period_end = None
    if tax_period_end_raw:
        try:
            tax_period_end = datetime.strptime(tax_period_end_raw, "%Y-%m-%d").date()
        except ValueError as e:
            print(f"Invalid date format for TaxPeriodEndDt: {tax_period_end_raw}. Error: {e}")

    tax_period_start = None  # Add logic to extract if available

    return {
        'return_id': return_id,
        'tax_year': tax_year,
        'return_type': return_type,
        'tax_period_start': tax_period_start,
        'tax_period_end': tax_period_end
    }


def insert_returns(conn, data):
    """
    Insert data into the `returns` table and return the generated ID.
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO returns (return_id, tax_year, return_type, tax_period_start, tax_period_end)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (
        data['return_id'], data['tax_year'], data['return_type'], data['tax_period_start'], data['tax_period_end']))
        return cur.fetchone()[0]
