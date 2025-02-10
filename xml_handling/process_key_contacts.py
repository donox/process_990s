import psycopg2


def handler(mg_trans, return_id, root, file_path):
    """
    Handler for processing key contacts data.

    Args:
        mg_trans: DB transaction object
        return_id: The ID of the `returns` table entry.
        root: The XML root element.
        file_path: (unused - for compatibility with other handlers)

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # First get the EIN from the Return table
        query = "SELECT EIN FROM return WHERE ReturnId = %s"
        params = (return_id,)
        result = mg_trans.execute(query, params=params)
        if not result:
            print(f"Error: Return ID {return_id} not found")
            raise ValueError(f"Return with ID: {return_id} not found")
        ein = result[0]

        contacts = root.findall('./ReturnData/IRS990PF/OfficerDirTrstKeyEmplInfoGrp/OfficerDirTrstKeyEmplGrp')
        if not contacts:
            return None

        contacts_data = extract_key_contacts(root)
        if not contacts_data:
            return None

        insert_key_contacts(mg_trans, contacts_data, ein)
        return True

    except Exception as e:
        print(f"Error processing key contacts for return ID {return_id}: {e}")
        return False


def extract_key_contacts(root):
    """
    Extract data for the `key_contacts` table from the XML file.
    """
    contacts = root.findall('./ReturnData/IRS990PF/OfficerDirTrstKeyEmplInfoGrp/OfficerDirTrstKeyEmplGrp')
    if not contacts:
        return None

    results = []
    for contact in contacts:
        contact_data = {
            'person_name': contact.findtext('./PersonNm', default=""),
            'address_line1': contact.findtext('./USAddress/AddressLine1Txt', default=""),
            'city': contact.findtext('./USAddress/CityNm', default=""),
            'state': contact.findtext('./USAddress/StateAbbreviationCd', default=""),
            'zip': contact.findtext('./USAddress/ZIPCd', default=""),
            'title': contact.findtext('./TitleTxt', default=""),
            'average_hours': float(contact.findtext('./AverageHrsPerWkDevotedToPosRt', default="0.0")),
            'compensation': float(contact.findtext('./CompensationAmt', default="0")),
            'employee_benefits': float(contact.findtext('./EmployeeBenefitProgramAmt', default="0")),
            'expense_account': float(contact.findtext('./ExpenseAccountOtherAllwncAmt', default="0"))
        }
        results.append(contact_data)

    return results


def insert_key_contacts(mg_trans, data, ein):
    """
    Insert data into the key_contacts table.
    """
    try:
        for contact in data:
            query = """
                INSERT INTO keycontacts (
                    EIN, PersonName, AddressLine1, City, State, ZipCode,
                    Title, AverageHoursPerWeek, Compensation, EmployeeBenefits,
                    ExpenseAccount
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (EIN, PersonName) DO NOTHING;
            """
            params = (
                ein,
                contact['person_name'],
                contact['address_line1'],
                contact['city'],
                contact['state'],
                contact['zip'],
                contact['title'],
                contact['average_hours'],
                contact['compensation'],
                contact['employee_benefits'],
                contact['expense_account']
            )
            result = mg_trans.execute(query, params=params)
            if not result:
                raise ValueError(f"key contact {contact['person_name']} failed.")
    except Exception as e:
        print(f"Error on insert to key_contact: {e}")
        raise e
