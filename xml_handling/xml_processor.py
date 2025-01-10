import os
from datetime import datetime
import psycopg2
import importlib
import re
import xml.etree.ElementTree as ET
from xml_handling.process_return import *
from xml_handling.process_filer import *
from xml_handling.process_financials import *
from xml_handling.process_investments import *


def parse_and_insert(file_path, conn, modules):
    """
    Parse an XML file and insert data into the database, delegating
    table-specific operations to provided handler modules.

    Args:
        file_path (str): Path to the XML file.
        conn: psycopg2 connection object.
        modules (list): List of handler modules for specific tables.

    Returns:
        None
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract and insert filer
        filer_data = extract_filer(root)
        if filer_data:
            insert_filer(conn, filer_data)

        # Extract and insert returns
        return_id = process_returns(file_path, root, conn)

        # Process each module
        for module in modules:
            # Call the module's handler function
            handler_result = module.handler(conn, return_id, root)
            if not handler_result:
                print(f"Handler for module {module.__name__} failed.")

        # Commit the transaction after processing all modules
        conn.commit()
        print(f"Successfully processed file: {file_path}")

    except Exception as e:
        conn.rollback()
        print(f"Error processing file {file_path}: {e}")


def process_returns(file_path, root, conn):
    """
    Extract and insert data for the `Return` table.

    Args:
        file_path (str): Path to the XML file.
        root: The XML root element.
        conn: psycopg2 connection object.

    Returns:
        int: The database ID for the inserted return row.
    """
    # Extract data from <ReturnHeader>
    return_ts_raw = root.findtext('ReturnTs', default=None)
    return_ts = None
    if return_ts_raw:
        try:
            return_ts = datetime.fromisoformat(return_ts_raw)
        except ValueError as e:
            print(f"Invalid timestamp format for ReturnTs: {return_ts_raw}. Error: {e}")

    tax_period_end_raw = root.findtext('TaxPeriodEndDt', default=None)
    tax_period_end = None
    if tax_period_end_raw:
        try:
            tax_period_end = datetime.strptime(tax_period_end_raw, "%Y-%m-%d").date()
        except ValueError as e:
            print(f"Invalid date format for TaxPeriodEndDt: {tax_period_end_raw}. Error: {e}")

    tax_period_begin_raw = root.findtext('TaxPeriodBeginDt', default=None)
    tax_period_begin = None
    if tax_period_begin_raw:
        try:
            tax_period_begin = datetime.strptime(tax_period_begin_raw, "%Y-%m-%d").date()
        except ValueError as e:
            print(f"Invalid date format for TaxPeriodBeginDt: {tax_period_begin_raw}. Error: {e}")

    return_type = root.findtext('ReturnTypeCd', default=None)
    tax_year = root.findtext('TaxYr', default=None)
    tax_year = int(tax_year) if tax_year and tax_year.isdigit() else None

    # Extract data from IRS990PF
    organization_501c3_exempt_raw = root.findtext('IRS990PF/Organization501c3ExemptPFInd', default=None)
    organization_501c3_exempt = organization_501c3_exempt_raw == 'X'

    fmv_assets_eoy_raw = root.findtext('IRS990PF/FMVAssetsEOYAmt', default=None)
    fmv_assets_eoy = float(fmv_assets_eoy_raw) if fmv_assets_eoy_raw else None

    method_of_accounting_cash_raw = root.findtext('IRS990PF/MethodOfAccountingCashInd', default=None)
    method_of_accounting_cash = method_of_accounting_cash_raw == 'X'

    # Extract EIN from <ReturnHeader>
    filer_ein = root.findtext('EIN', default=None)
    if not filer_ein:
        raise ValueError("Filer EIN is missing, and it is required for the Return table.")

    # Insert data into the `Return` table
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Return (
                EIN, TaxPeriodEnd, TaxPeriodBegin, ReturnTs, ReturnType, TaxYear, BuildTs,
                Organization501c3ExemptPF, FMVAssetsEOY, MethodOfAccountingCash
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s)
            RETURNING ReturnId;
        """, (filer_ein, tax_period_end, tax_period_begin, return_ts, return_type, tax_year,
              organization_501c3_exempt, fmv_assets_eoy, method_of_accounting_cash))
        return cur.fetchone()[0]  # Return the inserted row's ID



def process_directory(directory, conn):
    """
    Process all XML files in a directory using dynamically loaded modules.

    Args:
        directory (str): Directory containing XML files.
        conn: psycopg2 connection object.

    Returns:
        None
    """
    # Dynamically load modules
    modules = load_modules()

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                parse_and_insert(file_path, conn, modules)


def load_modules():
    """
    Dynamically load handler modules in same directory as this processor.

    Returns:
        list: List of loaded modules.
    """
    module_path = os.path.dirname(__file__)
    module_names = find_process_modules(directory=module_path)
    loaded_modules = []
    for module_name in module_names:
        module_file = os.path.join(module_path, f"{module_name}.py")
        if os.path.exists(module_file):
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            loaded_modules.append(module)
        else:
            print(f"Module '{module_name}' not found in path: {module_path}")
    return loaded_modules


def find_process_modules(directory="."):
    """
    Scans the specified directory and finds all modules of the form 'process_xxx.py'.

    Args:
        directory (str): The directory to scan. Defaults to the current directory.

    Returns:
        list: A list of module names (without the .py extension) that match the pattern.
    """
    module_pattern = re.compile(r"^process_[a-zA-Z0-9_]+\.py$")
    modules = []

    # Scan the directory
    for file_name in os.listdir(directory):
        if module_pattern.match(file_name):
            # Remove the .py extension
            module_name = os.path.splitext(file_name)[0]
            modules.append(module_name)

    return modules
