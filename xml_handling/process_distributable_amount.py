import psycopg2
import xml.etree.ElementTree as ET
from src.main import add_unhandled


def handler(conn, return_id, root, file_path):
    """
    Handler for processing distributable amount data.
    Extracts data from the XML and inserts it into the `distributableamount` table.

    Args:
        conn: psycopg2 connection object.
        return_id: The ID of the `returns` table entry.
        root: The XML root element.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Extract distributable amount data
        base_element = root.find('./ReturnData/IRS990PF/DistributableAmountGrp')
        if base_element is None:
            return None

        distributable_amount = extract_distributable_amount(base_element, file_path)
        if not distributable_amount:
            return None

            # Insert grants and contributions data
        insert_distributable_amount(conn, return_id, distributable_amount)
        return True

    except Exception as e:
        print(f"Error processing grants and contributions for return ID {return_id}: {e}")
        return False


def extract_distributable_amount(base_element, file_path):
    """
    Extract data for the `distributableamount` table from the XML file.
    """

    min_return = base_element.findtext('./MinimumInvestmentReturnAmt', default=None)
    investment_tax = base_element.findtext('./TaxBasedOnInvestmentIncomeAmt', default=None)
    total_tax = base_element.findtext('./TotalTaxAmt', default=None)
    amt_before_adjust = base_element.findtext('./DistributableBeforeAdjAmt', default=None)
    amt_before_deduction = base_element.findtext('./DistributableBeforeDedAmt', default=None)
    adjusted_amt = base_element.findtext('./DistributableAsAdjustedAmt', default=None)
    if adjusted_amt is None:            # Indicator that none of the group are present
        for elem in base_element:
            add_unhandled(file_path, elem.tag)
        return None

    return {
        'min_return': min_return,
        'investment_tax': investment_tax,
        'total_tax': total_tax,
        'amt_before_adjust': amt_before_adjust,
        'amt_before_deduction': amt_before_deduction,
        'adjusted_amt': adjusted_amt,
    }


def insert_distributable_amount(conn, return_id, data):
    """
    Insert data into the `distributableamount` table.

    Args:
        conn: psycopg2 connection object.
        return_id: The ID of the `returns` table entry.
        data: A dictionary containing distributable amount data.

    Returns:
        None
    """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO distributableamount (returnid, minimuminvestmentreturn, taxbasedoninvestmentincome,
                 totaltax, distributablebeforeadj, distributablebeforeded, distributableasadjusted)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (return_id, int(data['min_return']), int(data['investment_tax']), int(data['total_tax']),
                  int(data['amt_before_adjust']), int(data['amt_before_deduction']), int(data['adjusted_amt'])))
    except Exception as e:
        print(f"Error on insert to grants_and_contributions: {e}")
