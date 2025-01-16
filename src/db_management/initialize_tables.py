import os


def table_exists(conn, table_name):
    """
    Check if a table exists in the database.
    """
    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = %s
        );
    """
    with conn.cursor() as cur:
        cur.execute(query, (table_name,))
        return cur.fetchone()[0]


def get_table_schema(conn, table_name):
    """
    Get the schema of an existing table.
    """
    query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (table_name,))
        return {row[0]: row[1] for row in cur.fetchall()}


def compare_schemas(existing_schema, desired_schema):
    """
    Compare the existing schema with the desired schema.

    Args:
        existing_schema (dict): Current table schema (column names as keys, types as values).
        desired_schema (dict): Schema from the DDL.

    Returns:
        tuple: Two lists:
            - columns_to_add (list of tuples): Columns missing from the existing schema.
            - columns_with_mismatched_types (list of tuples): Columns with mismatched types.
    """
    columns_to_add = []
    columns_with_mismatched_types = []

    # Normalize existing schema keys for case insensitivity
    normalized_existing_schema = {col_name.lower(): col_type.lower() for col_name, col_type in existing_schema.items()}

    for col_name, col_type in desired_schema.items():
        col_name_lower = col_name.lower()
        col_type_lower = col_type.lower()

        if col_name_lower not in normalized_existing_schema:
            # Column is missing, needs to be added
            columns_to_add.append((col_name, col_type))
        elif normalized_existing_schema[col_name_lower] != col_type_lower:
            # Column exists but has a mismatched type
            columns_with_mismatched_types.append((col_name, normalized_existing_schema[col_name_lower], col_type))

    return columns_to_add, columns_with_mismatched_types


def apply_modifications(conn, ddl_file, table_name, force=False):
    """
    BROKEN!!!  Can't handle modifications
    Modify the schema of an existing table to match the DDL.

    Args:
        conn: psycopg2 connection object.
        ddl_file (str): Path to the DDL file.
        table_name (str): Name of the table to modify.
        force (bool): If True, apply changes for mismatched types. Default is False.

    Raises:
        ValueError: If modifications would result in data loss and force=False.
    """
    print(f"Modifying table: {table_name}")
    force = True

    # Get the desired schema from the DDL
    desired_schema = parse_ddl_safe(ddl_file)

    # Get the existing schema from the database
    existing_schema = get_table_schema(conn, table_name)

    # Compare schemas
    columns_to_add, columns_with_mismatched_types = compare_schemas(existing_schema, desired_schema)

    # Handle mismatched columns
    if columns_with_mismatched_types and not force:
        for col_name, existing_type, desired_type in columns_with_mismatched_types:
            print(f"Column '{col_name}' type mismatch: {existing_type} (existing) vs {desired_type} (desired).")
        raise ValueError("Schema modification failed due to type mismatches. Use force=True to override.")

    if columns_with_mismatched_types and force:
        try:
            with conn.cursor() as cur:
                for col_name, existing_type, desired_type in columns_with_mismatched_types:
                    print(f"Altering column '{col_name}' from type '{existing_type}' to '{desired_type}'.")
                    alter_stmt = f"ALTER TABLE {table_name} ALTER COLUMN {col_name} TYPE {desired_type};"
                    cur.execute(alter_stmt)
            conn.commit()
            print(f"Forced modifications applied to columns with mismatched types in table: {table_name}")
        except Exception as e:
            conn.rollback()
            print(f"Failed to modify mismatched columns in table {table_name}. Error: {e}")

    # Apply modifications for missing columns
    if columns_to_add:
        try:
            with conn.cursor() as cur:
                for col_name, col_type in columns_to_add:
                    print(f"Adding column '{col_name}' with type '{col_type}' to table '{table_name}'.")
                    alter_stmt = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"
                    cur.execute(alter_stmt)
            conn.commit()
            print(f"Columns added to table: {table_name}")
        except Exception as e:
            conn.rollback()
            print(f"Failed to add columns to table {table_name}. Error: {e}")

    # If no changes are needed
    if not columns_to_add and not columns_with_mismatched_types:
        print(f"No modifications required for table: {table_name}.")


def parse_ddl_safe(ddl_file):
    """
    Safely parse a DDL file to extract the schema as a dictionary.

    Args:
        ddl_file (str): Path to the DDL file.

    Returns:
        dict: A dictionary mapping column names to data types.
    """
    schema = {}
    with open(ddl_file, 'r') as file:
        lines = file.readlines()

    inside_create_table = False
    for line in lines:
        line = line.strip()

        # Detect CREATE TABLE statement
        if line.upper().startswith("CREATE TABLE"):
            inside_create_table = True
            continue

        # End of table definition
        if inside_create_table and line == ");":
            break

        # Parse column definitions
        if inside_create_table:
            # Ignore empty lines and comments
            if not line or line.startswith("--"):
                continue

            # Extract column name and type
            parts = line.split()
            if len(parts) >= 2:
                column_name = parts[0].strip('"')
                column_type = " ".join(parts[1:]).rstrip(",")
                schema[column_name] = column_type

    return schema


def initialize_tables(conn, ddl_dir):
    """
    Initialize or modify database tables based on DDL scripts.
    """
    table_ddl_files = {
        # "filer": os.path.join(ddl_dir, "filer.sql"),        # DONE
        # "return": os.path.join(ddl_dir, "return.sql"),        # DONE
        # "accounting_fees": os.path.join(ddl_dir, "accounting_fees.sql"),
        # "asset_sales": os.path.join(ddl_dir, "asset_sales.sql"),
        # "business_officer": os.path.join(ddl_dir, "business_officer.sql"),
        # "compensation": os.path.join(ddl_dir, "compensation.sql"),       # DONE
        # "distributable_amount": os.path.join(ddl_dir, "distributable_amount.sql"),        # DONE
        # "excise_tax": os.path.join(ddl_dir, "excise_tax.sql"),
        # "expenses": os.path.join(ddl_dir, "expenses.sql"),  # DONE
        # "grants_and_contributions": os.path.join(ddl_dir, "grants_and_contributions.sql"),        # DONE
        # "investments": os.path.join(ddl_dir, "investments.sql"),        # DONE
        # "minimum_investment_return": os.path.join(ddl_dir, "minimum_investment_return.sql"),
        # "other_expenses": os.path.join(ddl_dir, "other_expenses.sql"),
        # "preparer_firm": os.path.join(ddl_dir, "preparer_firm.sql"),
        # "preparer_person": os.path.join(ddl_dir, "preparer_person.sql"),
        # "qualifying_distributions": os.path.join(ddl_dir, "qualifying_distributions.sql"),        # DONE
        # "return_balance_sheet": os.path.join(ddl_dir, "return_balance_sheet.sql"),        # DONE
        # "return_preparer": os.path.join(ddl_dir, "return_preparer.sql"),
        # "signing_officer": os.path.join(ddl_dir, "signing_officer.sql"),
        # "statement_regarding_activities": os.path.join(ddl_dir, "statement_regarding_activities.sql"),
        # "statements_regarding_activities": os.path.join(ddl_dir, "statements_regarding_activities.sql"),
        # "supplementary_information": os.path.join(ddl_dir, "supplementary_information.sql"),         # DONE
        # "taxes_detail": os.path.join(ddl_dir, "taxes_detail.sql"),
        # "undistributed_income": os.path.join(ddl_dir, "undistributed_income.sql"),        # DONE
    }

    for table_name, ddl_file in table_ddl_files.items():
        if table_exists(conn, table_name):
            print(f"Table '{table_name}' exists. Checking schema...")
            current_schema = get_table_schema(conn, table_name)
            print(f"Current schema for '{table_name}': {current_schema}")

            # Here you can check if the schema matches your expected schema and apply modifications if needed
            apply_modifications(conn, ddl_file, table_name)

        else:
            print(f"Table '{table_name}' does not exist. Creating...")
            try:
                with conn.cursor() as cur:
                    with open(ddl_file, 'r') as ddl:
                        cur.execute(ddl.read())
                conn.commit()
                print(f"Table '{table_name}' created successfully.")
            except Exception as e:
                conn.rollback()
                print(f"Failed to create table {table_name}. Error: {e}")

