import psycopg2
from src.main import add_unhandled


def handler(mg_trans, return_id, root, file_path):
    """
    Handler for processing supplementary information data.

    Args:
        mg_trans: DB transaction object
        return_id: The ID of the `returns` table entry.
        root: The XML root element.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        base_element = root.find('./ReturnData/IRS990PF/SupplementaryInformationGrp')
        if base_element is None:
            return True             # handler succeed but nothing to do

        supp_info = extract_supplementary_info(base_element, file_path)
        if not supp_info:
            return True              # handler succeed but no info in group

        insert_supplementary_info(mg_trans, return_id, supp_info)
        return True

    except Exception as e:
        print(f"Error processing supplementary information for return ID {return_id}: {e}")
        return False


def extract_supplementary_info(base_element, file_path):
    """
    Extract supplementary information from the XML.
    """
    app_info = base_element.find('./ApplicationSubmissionInfoGrp')

    form_info = app_info.findtext('./FormAndInfoAndMaterialsTxt') if app_info is not None else None
    deadlines = app_info.findtext('./SubmissionDeadlinesTxt') if app_info is not None else None
    restrictions = app_info.findtext('./RestrictionsOnAwardsTxt') if app_info is not None else None
    email = app_info.findtext('./RecipientEmailAddressTxt') if app_info is not None else None

    total_paid = base_element.findtext('./TotalGrantOrContriPdDurYrAmt')
    total_future = base_element.findtext('./TotalGrantOrContriApprvFutAmt')
    preselected = base_element.findtext('./OnlyContriToPreselectedInd')

    # Check for unhandled elements
    for elem in base_element:
        if elem.tag not in ['ApplicationSubmissionInfoGrp', 'TotalGrantOrContriPdDurYrAmt',
                            'TotalGrantOrContriApprvFutAmt', 'OnlyContriToPreselectedInd']:
            add_unhandled(file_path, elem.tag)

    return {
        'form_info': form_info,
        'deadlines': deadlines,
        'restrictions': restrictions,
        'email': email,
        'total_paid': total_paid,
        'total_future': total_future,
        'preselected': preselected == 'X'
    }


def insert_supplementary_info(mg_trans, return_id, data):
    """
    Insert data into the supplementaryinformation table.
    """
    try:
        query = """
            INSERT INTO supplementaryinformation (
                returnid, applicationforminfo, applicationdeadlines, 
                applicationrestrictions, applicationemail,
                totalgrantspaidduringyear, totalgrantsapprovedfuture,
                onlypreselectedcontributions
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (returnid) DO UPDATE SET
                applicationforminfo = EXCLUDED.applicationforminfo,
                applicationdeadlines = EXCLUDED.applicationdeadlines,
                applicationrestrictions = EXCLUDED.applicationrestrictions,
                applicationemail = EXCLUDED.applicationemail,
                totalgrantspaidduringyear = EXCLUDED.totalgrantspaidduringyear,
                totalgrantsapprovedfuture = EXCLUDED.totalgrantsapprovedfuture,
                onlypreselectedcontributions = EXCLUDED.onlypreselectedcontributions;

            """
        params = (
            return_id,
            data['form_info'],
            data['deadlines'],
            data['restrictions'],
            data['email'],
            float(data['total_paid']) if data['total_paid'] else None,
            float(data['total_future']) if data['total_future'] else None,
            data['preselected']
        )
        result = mg_trans.execute(query, params=params)
        if not result:
            raise ValueError(f"supplementary_information failed.")
    except Exception as e:
        print(f"Error on insert to supplementary_information: {e}")
        raise e
