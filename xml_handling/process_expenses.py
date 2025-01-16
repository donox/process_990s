import psycopg2
from src.main import add_unhandled


def handler(conn, return_id, root, file_path):
    """
    Handler for processing expense  data.
    """
    try:
        base_element = root.find('./ReturnData/IRS990PF/AnalysisOfRevenueAndExpenses')
        if base_element is None:
            return None

        expense_info = extract_expenses(base_element, file_path)
        if not expense_info:
            return None

        insert_expenses(conn, return_id, expense_info)
        return True

    except Exception as e:
        print(f"Error processing expense analysis for return ID {return_id}: {e}")
        return False


def extract_expenses(base_element, file_path):
    """
    Extract expense analysis from the XML.
    """
    compensation = base_element.findtext('./CompOfcrDirTrstRevAndExpnssAmt')
    operating = base_element.findtext('./TotOprExpensesRevAndExpnssAmt')
    contributions = base_element.findtext('./ContriPaidRevAndExpnssAmt')
    total = base_element.findtext('./TotalExpensesRevAndExpnssAmt')
    accounting = base_element.findtext('./AccountingFeesRevAndExpnssAmt')
    other = base_element.findtext('./OtherExpensesRevAndExpnssAmt')

    # Check for unhandled elements
    expected_tags = ['CompOfcrDirTrstRevAndExpnssAmt', 'TotOprExpensesRevAndExpnssAmt',
                     'ContriPaidRevAndExpnssAmt', 'TotalExpensesRevAndExpnssAmt',
                     'AccountingFeesRevAndExpnssAmt', 'OtherExpensesRevAndExpnssAmt']

    for elem in base_element:
        if elem.tag not in expected_tags:
            add_unhandled(file_path, elem.tag)

    return {
        'compensation': compensation,
        'operating': operating,
        'contributions': contributions,
        'total': total,
        'accounting': accounting,
        'other': other
    }


def insert_expenses(conn, return_id, data):
    """
    Insert data into the expenses table.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO expenses (
                    returnid, compensationamount, operatingexpenses,
                    contributionspaid, totalexpenses, accountingfees, otherexpenses
                ) VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                return_id,
                float(data['compensation']) if data['compensation'] else None,
                float(data['operating']) if data['operating'] else None,
                float(data['contributions']) if data['contributions'] else None,
                float(data['total']) if data['total'] else None,
                float(data['accounting']) if data['accounting'] else None,
                float(data['other']) if data['other'] else None
            ))
    except Exception as e:
        print(f"Error on insert to expenses: {e}")
