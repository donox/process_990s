import psycopg2
from src.main import add_unhandled


def handler(mg_trans, return_id, root, file_path):
    """
    Handler for processing expense  data.

    Args:
        mg_trans: DB transaction object
        return_id: The ID of the `returns` table entry.
        root: The XML root element.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        base_element = root.find('./ReturnData/IRS990PF/AnalysisOfRevenueAndExpenses')
        if base_element is None:
            return True

        expense_info = extract_expenses(base_element, file_path)
        if not expense_info:
            return True

        insert_expenses(mg_trans, return_id, expense_info)
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


def insert_expenses(mg_trans, return_id, data):
    """
    Insert data into the expenses table.
    """
    try:
        query = """
                INSERT INTO expenses (
                    returnid, compensationamount, operatingexpenses,
                    contributionspaid, totalexpenses, accountingfees, otherexpenses
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (returnid) DO UPDATE SET
                    compensationamount = EXCLUDED.compensationamount,
                    operatingexpenses = EXCLUDED.operatingexpenses,
                    contributionspaid = EXCLUDED.contributionspaid,
                    totalexpenses = EXCLUDED.totalexpenses,
                    accountingfees = EXCLUDED.accountingfees,
                    otherexpenses = EXCLUDED.otherexpenses;

            """
        params = (
            return_id,
            float(data['compensation']) if data['compensation'] else None,
            float(data['operating']) if data['operating'] else None,
            float(data['contributions']) if data['contributions'] else None,
            float(data['total']) if data['total'] else None,
            float(data['accounting']) if data['accounting'] else None,
            float(data['other']) if data['other'] else None
        )
        result = mg_trans.execute(query, params=params)
        if not result:
            raise ValueError(f"expenses failed.")
    except Exception as e:
        print(f"Error on insert to expenses: {e}")
        raise e
