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


def apply_modifications(conn, ddl_file, table_name):
    """
    Apply modifications to a table based on its DDL file.
    """
    print(f"Modifying table: {table_name}")

    with open(ddl_file, 'r') as ddl:
        modification_sql = ddl.read()

    try:
        with conn.cursor() as cur:
            cur.execute(modification_sql)
        conn.commit()
        print(f"Modifications applied to table: {table_name}")
    except Exception as e:
        conn.rollback()
        print(f"Failed to modify table {table_name}. Error: {e}")


def initialize_tables(conn, ddl_dir):
    """
    Initialize or modify database tables based on DDL scripts.
    """
    table_ddl_files = {
        "filer": os.path.join(ddl_dir, "filer.sql"),
        "return": os.path.join(ddl_dir, "return.sql"),
        "accounting_fees": os.path.join(ddl_dir, "accounting_fees.sql"),
        "asset_sales": os.path.join(ddl_dir, "asset_sales.sql"),
        "business_officer": os.path.join(ddl_dir, "business_officer.sql"),
        "distributable_amount": os.path.join(ddl_dir, "distributable_amount.sql"),
        "excise_tax": os.path.join(ddl_dir, "excise_tax.sql"),
        "grants_and_contributions": os.path.join(ddl_dir, "grants_and_contributions.sql"),
        "investments": os.path.join(ddl_dir, "investments.sql"),
        "minimum_investment_return": os.path.join(ddl_dir, "minimum_investment_return.sql"),
        "other_expenses": os.path.join(ddl_dir, "other_expenses.sql"),
        "preparer_firm": os.path.join(ddl_dir, "preparer_firm.sql"),
        "preparer_person": os.path.join(ddl_dir, "preparer_person.sql"),
        "qualifying_distributions": os.path.join(ddl_dir, "qualifying_distributions.sql"),
        "return_balance_sheet": os.path.join(ddl_dir, "return_balance_sheet.sql"),
        "return_preparer": os.path.join(ddl_dir, "return_preparer.sql"),
        "revenue_and_expenses": os.path.join(ddl_dir, "revenue_and_expenses.sql"),
        "signing_officer": os.path.join(ddl_dir, "signing_officer.sql"),
        "statement_regarding_activities": os.path.join(ddl_dir, "statement_regarding_activities.sql"),
        "statements_regarding_activities": os.path.join(ddl_dir, "statements_regarding_activities.sql"),
        "taxes_detail": os.path.join(ddl_dir, "taxes_detail.sql"),
        "undistributed_income": os.path.join(ddl_dir, "undistributed_income.sql"),
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

