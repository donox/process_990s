import os
from datetime import datetime
import psycopg2
import importlib
import re
import glob
import xml.etree.ElementTree as ET
from xml_handling.process_return import *
from xml_handling.process_filer import *
from xml_handling.process_qualifyingdistributions import *
from xml_handling.process_investments import *


def remove_namespaces_and_attributes(root):
    """
    Remove namespaces and attributes from the XML tree.

    Args:
        root: The root element of the XML tree.

    Returns:
        The XML tree with namespaces and attributes removed.
    """
    for elem in root.iter():
        # Remove namespaces from the tag
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]  # Keep only the local part of the tag
        # Remove all attributes
        elem.attrib.clear()
    return root


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
        root = remove_namespaces_and_attributes(root)

        # filer and return ddl requires non-standard handling as filer creates the foreign key needed by
        # return and return generates the foreign key needed by all other handlers.
        # Extract and insert filer
        filer_data = extract_filer(root)
        if filer_data:
            insert_filer(conn, filer_data)

        # Extract and insert returns
        return_data = extract_returns(root, file_path)
        if return_data:
            return_id = insert_returns(conn, return_data)
            try:
                with conn.cursor() as cur:
                    query = """
                            SELECT returnid from return
                             WHERE returnfile = %s;"""
                    params = (return_data["return_file"],)
                    actual_query = cur.mogrify(query, params).decode('utf-8')

                    cur.execute(query, params)
                    return_id = cur.fetchone()[0]
            except Exception as e:
                print(f"Error on insert to retrieval of return id in file: {file_path}\n {e}")
                foo = 3
                return

        # Process each module
        for module in modules:
            # Call the module's handler function
            handler_result = module.handler(conn, return_id, root, file_path)
            if not handler_result:
                print(f"Handler for module {module.__name__} failed.")

        # Commit the transaction after processing all modules
        conn.commit()
        # print(f"Successfully processed file: {file_path}")        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    except Exception as e:
        conn.rollback()
        print(f"Error processing file {file_path}: {e}")


def process_directory(directory, conn):
    """
    Process XML files in a directory structure matching the pattern:
    ./*year/expanded_zip_files/*/processed/*/*.xml

    Args:
        directory (str): Base directory to start the search.
        conn: psycopg2 connection object.

    Returns:
        None
    """
    # Define the years of interest
    years = ['2023', '2024']

    # Build the search pattern
    patterns = [os.path.join(directory, f"{year}/expanded_zip_files/*/processed/*/*.xml") for year in years]

    # Dynamically load modules
    modules = load_modules()

    file_count = 0
    # skip_count = 13
    # Iterate through each pattern and process matching files
    for pattern in patterns:
        try:
            for file_path in glob.glob(pattern, recursive=True):
                # Check if the file has the correct extension
                if file_path.endswith('.xml'):
                    # if skip_count > 0:
                    #     skip_count -= 1
                    #     continue
                    # Process the file
                    parse_and_insert(file_path, conn, modules)
                    file_count += 1                             # LIMIT ITERATION
                    if file_count > 1000000:
                        return
        except Exception as e:
            print(f"Error in traversing directory: {e}")
    print(f"Total Files Processed: {file_count}")


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
        if module_name not in ["process_return", "process_filer"]:
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
            # if module_name not in ["process_key_contacts",]:
            #     continue
            modules.append(module_name)

    return modules
