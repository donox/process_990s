import psycopg2


def handler(conn, return_id, root, file_path):
    """
    Handler for processing key contacts data.
    """
    try:
        # First get the EIN from the Return table
        with conn.cursor() as cur:
            cur.execute("SELECT EIN FROM return WHERE ReturnId = %s", (return_id,))
            result = cur.fetchone()
            if not result:
                print(f"Error: Return ID {return_id} not found")
                return None
            ein = result[0]

        contacts = root.findall('./ReturnData/IRS990PF/OfficerDirTrstKeyEmplInfoGrp/OfficerDirTrstKeyEmplGrp')
        if not contacts:
            return None

        contacts_data = extract_key_contacts(root)
        if not contacts_data:
            return None

        insert_key_contacts(conn, contacts_data, ein)
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


def insert_key_contacts(conn, data, ein):
    """
    Insert data into the key_contacts table.
    """
    try:
        with conn.cursor() as cur:
            for contact in data:
                try:
                    cur.execute("""
                        INSERT INTO keycontacts (
                            EIN, PersonName, AddressLine1, City, State, ZipCode,
                            Title, AverageHoursPerWeek, Compensation, EmployeeBenefits,
                            ExpenseAccount
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (EIN, PersonName) DO NOTHING;
                    """, (
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
                    ))
                except psycopg2.IntegrityError as e:
                    # Skip duplicates silently
                    conn.rollback()
                    continue
    except Exception as e:
        print(f"Error on insert to key_contacts: {e}")