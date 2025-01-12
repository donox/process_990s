import os
from datetime import datetime
import psycopg2
import xml.etree.ElementTree as ET


def handler(conn, return_id, root, file_path):
    """
    Handler for processing investments data.
    Extracts data from the XML and inserts it into the `investments` table.

    Args:
        conn: psycopg2 connection object.
        return_id: The ID of the `returns` table entry.
        root: The XML root element.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Extract investments data
        investments = extract_investments(root, file_path)
        if not investments:
            return True  # No data to process

        # Insert investments data
        insert_investments(conn, return_id, investments)
        return True

    except Exception as e:
        print(f"Error processing investments for return ID {return_id}: {e}")
        return False


def extract_investments(root, file_path):
    """
    Extract data for the `investments` table from the XML file.
    """
    investments = root.findall('./ReturnData/InvestmentsCorporateStockGrp')
    result = []
    for investment in investments:
        stock_name = investment.findtext('./StockNm', default="")
        eoy_book_value = investment.findtext('./EOYBookValueAmt', default="0")
        eoy_fmv = investment.findtext('./EOYFMVAmt', default="0")

        result.append({
            'stock_name': stock_name,
            'eoy_book_value': int(float(eoy_book_value)) if eoy_book_value else 0,
            'eoy_fmv': int(float(eoy_fmv)) if eoy_fmv else 0
        })

    return result


def insert_investments(conn, return_id, data):
    """
    Insert data into the `investments` table.
    """
    try:
        with conn.cursor() as cur:
            for investment in data:
                cur.execute("""
                    INSERT INTO investments (return_id, stock_name, eoy_book_value, eoy_fmv)
                    VALUES (%s, %s, %s, %s);
                """, (return_id, investment['stock_name'], investment['eoy_book_value'], investment['eoy_fmv']))
    except Exception as e:
        print(f"Error on insert to invstements: {e}")
