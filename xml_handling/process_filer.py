import os
from datetime import datetime
import psycopg2
import xml.etree.ElementTree as ET


def extract_filer(root):
    """
    Extract data for the `filer` table from the XML file.
    """
    filer = root.find('./ReturnHeader/Filer')
    if filer is None:
        return None

    return {
        'ein': filer.findtext('./EIN', default=""),
        'business_name_line1': filer.findtext('./BusinessName/BusinessNameLine1Txt', default=""),
        'business_name_line2': filer.findtext('./BusinessName/BusinessNameLine2Txt', default=""),
        'phone_number': filer.findtext('./PhoneNum', default=""),
        'address_line1': filer.findtext('./USAddress/AddressLine1Txt', default=""),
        'city': filer.findtext('./USAddress/CityNm', default=""),
        'state': filer.findtext('./USAddress/StateAbbreviationCd', default=""),
        'zip': filer.findtext('./USAddress/ZIPCd', default="")
    }


def insert_filer(mg_trans, data):
    """
    Insert data into the `filer` table. If the EIN already exists, print a message and compare columns.

    Args:
        mg_trans: db connection object.
        data: A dictionary containing the data to insert.
    """
    try:
        query = """
                INSERT INTO filer (EIN, BusinessNameLine1, BusinessNameLine2, PhoneNum,
                                   AddressLine1, City, State, ZIPCode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (EIN) 
                DO UPDATE SET
                   BusinessNameLine1 = EXCLUDED.BusinessNameLine1,
                   BusinessNameLine2 = EXCLUDED.BusinessNameLine2, 
                   PhoneNum = EXCLUDED.PhoneNum,
                   AddressLine1 = EXCLUDED.AddressLine1,
                   City = EXCLUDED.City,
                   State = EXCLUDED.State,
                   ZIPCode = EXCLUDED.ZIPCode
                RETURNING EIN;
            """
        params = (data['ein'], data['business_name_line1'], data['business_name_line2'],
                  data['phone_number'], data['address_line1'], data['city'], data['state'], data['zip'])
        result = mg_trans.execute_independent(query, params)
        return result
    except Exception as e:
        print(f"Error in process_filer on insert. {e}")
        raise e
