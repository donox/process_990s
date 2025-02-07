import psycopg2
import xml.etree.ElementTree as ET
from src.main import add_unhandled


def handler(conn, return_id, root, file_path):
    """
    Handler for processing grants and contributions data.
    Extracts data from the XML and inserts it into the `grants_and_contributions` table.

    Args:
        conn: psycopg2 connection object.
        return_id: The ID of the `returns` table entry.
        root: The XML root element.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Extract grants and contributions data
        base_elements = root.find('./ReturnData/IRS990PF/SupplementaryInformationGrp')
        if base_elements is None:
            return None

        for base_element in base_elements:
            grants_and_contributions = extract_grants_and_contributions(base_element, file_path)
            if not grants_and_contributions:
                continue

            # Insert grants and contributions data
            insert_grants_and_contributions(conn, return_id, grants_and_contributions)
        return True

    except Exception as e:
        print(f"Error processing grants and contributions for return ID {return_id}: {e}")
        return False


def extract_grants_and_contributions(base_element, file_path):
    """
    Extract data for the `grants_and_contributions` table from the XML file.
    """
    if base_element.tag == 'GrantOrContributionPdDurYrGrp':
        grants_data = base_element.find('.')
        if grants_data is None:
            return None
    else:
        add_unhandled(file_path, base_element.tag)
        return None

    recipient_name = grants_data.findtext('./RecipientBusinessName/BusinessNameLine1Txt', default=None)
    recipient_address = grants_data.findtext('./RecipientUSAddress/AddressLine1Txt', default=None)
    recipient_city = grants_data.findtext('./RecipientUSAddress/CityNm', default=None)
    recipient_state = grants_data.findtext('./RecipientUSAddress/StateAbbreviationCd', default=None)
    recipient_zip = grants_data.findtext('./RecipientUSAddress/ZIPCd', default=None)
    recipient_relationship = grants_data.findtext('./RecipientRelationshipTxt', default=None)
    purpose = grants_data.findtext('./GrantOrContributionPurposeTxt', default=None)
    amount = grants_data.findtext('./Amt', default="0")

    return {
        'recipient_name': recipient_name,
        'recipient_address': recipient_address,
        'recipient_city': recipient_city,
        'recipient_state': recipient_state,
        'recipient_zip': recipient_zip,
        'recipient_relationship': recipient_relationship,
        'amount': int(float(amount)) if amount else 0,
        'purpose': purpose
    }


def insert_grants_and_contributions(conn, return_id, data):
    """
    Insert data into the `grants_and_contributions` table.

    Args:
        conn: psycopg2 connection object.
        return_id: The ID of the `returns` table entry.
        data: A dictionary containing grants and contributions data.

    Returns:
        None
    """
    try:
        with conn.cursor() as cur:
            query = """
                INSERT INTO grantsandcontributions (returnid, recipientname, addressline1, city, state, zipcode,
                 recipientrelationship, purpose, amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            params = (return_id, data['recipient_name'], data['recipient_address'], data['recipient_city'],
                  data['recipient_state'], data['recipient_zip'], data['recipient_relationship'], data['purpose'],
                  data['amount'])
            actual_query = cur.mogrify(query, params).decode('utf-8')
            cur.execute(query, params)
            if cur.statusmessage != "INSERT 0 1":
                print(f"Unexpected status in process_grants_and_contributions: {cur.statusmessage}")
                conn.rollback()
            else:
                conn.commit()
    except Exception as e:
        print(f"Error on insert to grants_and_contributions: {e}")
        conn.rollback()
