# queries/__init__.py
from importlib import import_module
from pathlib import Path
import os

QUERIES = {}

# Dynamically import all query files in this directory
query_dir = Path(__file__).parent
for file in query_dir.glob('*_queries.py'):
    module_name = file.stem  # filename without extension
    module = import_module(f'.{module_name}', package='reports.data_sources.queries')
    QUERIES.update(getattr(module, 'QUERIES', {}))