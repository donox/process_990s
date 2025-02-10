import importlib
import re
import glob
import traceback
from xml_handling.process_return import *
from xml_handling.process_filer import *
from src.db_management.manage_transactions import DBTransaction


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


def parse_and_insert(file_path, config, modules):
    """
    Parse an XML file and insert data into the database, delegating
    table-specific operations to provided handler modules.

    Args:
        file_path (str): Path to the XML file.
        config: configuration which is needed to create DBTransaction
        modules (list): List of handler modules for specific tables.

    Returns:
        None
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        root = remove_namespaces_and_attributes(root)
        mg_trans = DBTransaction(config)

        # filer and return ddl requires non-standard handling as filer creates the foreign key needed by
        # return and return generates the foreign key needed by all other handlers.
        # Extract and insert filer
        filer_data = extract_filer(root)
        if filer_data:
            insert_filer(mg_trans, filer_data)

        # Extract and insert returns
        return_data = extract_returns(root, file_path)
        if return_data:
            try:
                return_id = insert_returns(mg_trans, return_data)
                # IS THERE A CASE WHERE THIS IS NEEDED?
                # query = """
                #         SELECT returnid from return
                #          WHERE returnfile = %s;"""
                # params = (return_data["return_file"],)
                # result = mg_trans.execute(query, params=params)
                # if result:
                #     return_id = result[0]
                # else:
                #     raise ValueError("No result when seeking returnid")
            except Exception as e:
                print(f"Error on insert to retrieval of return id in file: {file_path}\n {e}")
                mg_trans.rollback()
                return

        # Process each module
        for module in modules:
            # Call the module's handler function
            handler_result = module.handler(mg_trans, return_id, root, file_path)
            if not handler_result:
                raise ValueError(f"Handler for module {module.__name__} failed.")

        # Commit the transaction after processing all modules
        mg_trans.commit()
        # print(f"Successfully processed file: {file_path}")        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    except Exception as e:
        mg_trans.rollback()
        print(f"Error processing file {file_path}: {e}\n {traceback.format_exc()}")


def process_directory(directory, config):
    """
    Process XML files in a directory structure matching the pattern:
    ./*year/expanded_zip_files/*/processed/*/*.xml

    Args:
        directory (str): Base directory to start the search.
        config: configuration needed to create db connection

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
    # All tables except filer execute in single transaction defined by mg_trans object
    for pattern in patterns:
        try:
            for file_path in glob.glob(pattern, recursive=True):
                # Check if the file has the correct extension
                if file_path.endswith('.xml'):
                    # if skip_count > 0:
                    #     skip_count -= 1
                    #     continue
                    # Process the file
                    parse_and_insert(file_path, config, modules)
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
            if os.path.exists(module_file) and False:       # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
