from src.main import add_unhandled


def handler(mg_trans, return_id, root, file_path):
    """
    Handler for processing compensation information data.

    Args:
        mg_trans: DB transaction object
        return_id: The ID of the `returns` table entry.
        root: The XML root element.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        base_element = root.find('./ReturnData/IRS990PF/OfficerDirTrstKeyEmplInfoGrp')
        if base_element is None:
            return True

        comp_info = extract_compensation_info(base_element, file_path)
        if not comp_info:
            return True

        insert_compensation_info(mg_trans, return_id, comp_info)
        return True

    except Exception as e:
        print(f"Error processing compensation information for return ID {return_id}: {e}")
        return False


def extract_compensation_info(base_element, file_path):
    """
    Extract compensation information from the XML.
    """
    compensation_data = []

    # Process each officer/director/trustee
    for officer in base_element.findall('./OfficerDirTrstKeyEmplGrp'):
        person_info = {
            'name': officer.findtext('./PersonNm'),
            'title': officer.findtext('./TitleTxt'),
            'hours': officer.findtext('./AverageHrsPerWkDevotedToPosRt'),
            'compensation': officer.findtext('./CompensationAmt'),
            'benefits': officer.findtext('./EmployeeBenefitProgramAmt'),
            'expenses': officer.findtext('./ExpenseAccountOtherAllwncAmt')
        }
        compensation_data.append(person_info)

    # Get highest paid information
    highest_paid_emp = base_element.findtext('./CompOfHghstPdEmplOrNONETxt')
    highest_paid_cont = base_element.findtext('./CompOfHghstPdCntrctOrNONETxt')

    # Check for unhandled elements
    for elem in base_element:
        if elem.tag not in ['OfficerDirTrstKeyEmplGrp',
                            'CompOfHghstPdEmplOrNONETxt',
                            'CompOfHghstPdCntrctOrNONETxt']:
            add_unhandled(file_path, elem.tag)

    return {
        'officers': compensation_data,
        'highest_paid_employee': highest_paid_emp,
        'highest_paid_contractor': highest_paid_cont
    }


def insert_compensation_info(mg_trans, return_id, data):
    """
    Insert data into the compensation table.
    """
    try:
        for officer in data['officers']:
            query = """
                INSERT INTO compensation (
                    returnid, personname, title, averagehours, 
                    compensation, employeebenefits, expenseaccount,
                    highestpaidemployeeinfo, highestpaidcontractorinfo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (returnid, personname) DO UPDATE SET
                    personname = EXCLUDED.personname,
                    title = EXCLUDED.title,
                    averagehours = EXCLUDED.averagehours,
                    compensation = EXCLUDED.compensation,
                    employeebenefits = EXCLUDED.employeebenefits,
                    expenseaccount = EXCLUDED.expenseaccount,
                    highestpaidemployeeinfo = EXCLUDED.highestpaidemployeeinfo,
                    highestpaidcontractorinfo = EXCLUDED.highestpaidcontractorinfo;

            """
            params = (
                return_id,
                officer['name'],
                officer['title'],
                float(officer['hours']) if officer['hours'] else None,
                float(officer['compensation']) if officer['compensation'] else None,
                float(officer['benefits']) if officer['benefits'] else None,
                float(officer['expenses']) if officer['expenses'] else None,
                data['highest_paid_employee'],
                data['highest_paid_contractor']
            )
            result = mg_trans.execute(query, params=params)
            if not result:
                raise ValueError(f"compensation for {officer['name']} failed.")
    except Exception as e:
        print(f"Error on insert to compensation: {e}")
        raise e
