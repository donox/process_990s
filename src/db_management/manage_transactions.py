import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from io import StringIO
import csv
from typing import Optional, List
from src.db_management.manage_config import connect_to_db


class DBTransaction:
    def __init__(self, config):
        self.config = config
        self.conn = connect_to_db(self.config)
        self.cur = None
        self.transaction_log = []
        self.in_transaction = False  # Track if a transaction is active

    def execute(self, query: str, params: tuple = None) -> Optional[List[tuple]]:
        """Execute a query within the current transaction"""
        try:
            if not self.cur:
                self.cur = self.conn.cursor()
                if not self.in_transaction:  # Start transaction if not already started
                    self.cur.execute("BEGIN")
                    self.in_transaction = True
                    self.transaction_log.append({
                        'timestamp': datetime.now(),
                        'operation': 'BEGIN',
                        'status': 'success'
                    })
            actual_query = self.cur.mogrify(query, params).decode('utf-8')
            self.transaction_log.append({
                'timestamp': datetime.now(),
                'query': actual_query,
                'status': 'pending'
            })
            self.cur.execute(query, params)
            self.transaction_log[-1].update({
                'status': 'success',
                'rowcount': self.cur.rowcount,
                'statusmessage': self.cur.statusmessage
            })
            if query.strip().upper().startswith('SELECT'):
                return self.cur.fetchall()
            if query.upper().find('RETURNING') != -1:
                return self.cur.fetchone()
            return True
        except Exception as e:
            self.transaction_log[-1].update({
                'status': 'failed',
                'error': str(e)
            })
            raise e

    def execute_independent(self, query: str, params: tuple = None):
        """Execute a single operation in its own transaction with its own connection"""
        with connect_to_db(self.config) as independent_conn:
            with independent_conn.cursor() as independent_cur:
                try:
                    independent_cur.execute(query, params)
                    if query.strip().upper().startswith('SELECT'):
                        result = independent_cur.fetchall()
                    elif query.upper().find('RETURNING') != -1:
                        result = independent_cur.fetchone()
                    else:
                        result = True
                    independent_conn.commit()
                    return result
                except Exception as e:
                    independent_conn.rollback()
                    raise e

    def copy_from_independent(self, data, table_name: str, columns: List[str]):
        """Use COPY FROM for very fast bulk inserts with independent connection"""
        if not table_name or not columns:
            raise ValueError("Table name and columns must be specified")

        with connect_to_db(self.config) as independent_conn:
            with independent_conn.cursor() as independent_cur:
                try:
                    # Verify table exists
                    independent_cur.execute(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
                        (table_name,)
                    )
                    if not independent_cur.fetchone()[0]:
                        raise ValueError(f"Table {table_name} does not exist")

                    with StringIO() as f:
                        writer = csv.writer(f)
                        writer.writerows(data)
                        f.seek(0)

                        independent_cur.copy_from(f, table_name, columns=columns, sep=',')
                        independent_conn.commit()
                except Exception as e:
                    independent_conn.rollback()
                    raise e

    def execute_values_independent(self, query: str, params_list: List[tuple], page_size: int = 1000):
        """Use execute_values for efficient bulk inserts with independent connection"""
        if not query.strip().upper().startswith('INSERT'):
            raise ValueError("Query must be an INSERT statement")

        if not params_list:
            raise ValueError("params_list cannot be empty")

        with connect_to_db(self.config) as independent_conn:
            with independent_conn.cursor() as independent_cur:
                try:
                    execute_values(
                        independent_cur,
                        query,
                        params_list,
                        page_size=page_size
                    )
                    independent_conn.commit()
                except Exception as e:
                    independent_conn.rollback()
                    raise e

    def commit(self):
        try:
            if self.cur: #check cursor exist before attempting commit
                self.conn.commit()
                self.transaction_log.append({
                    'timestamp': datetime.now(),
                    'operation': 'COMMIT',
                    'status': 'success'
                })
                self.cur.close()  # close cursor on commit
            self.cur = None  # Reset the cursor
            self.in_transaction = False
        except Exception as e:
            self.transaction_log.append({
               'timestamp': datetime.now(),
                'operation': 'COMMIT',
                'status': 'failed',
                'error': str(e)
            })
            raise e
    def rollback(self):
        try:
            if self.cur: #check cursor exist before attempting rollback
                self.conn.rollback()
                self.transaction_log.append({
                    'timestamp': datetime.now(),
                    'operation': 'ROLLBACK',
                    'status': 'success'
                })
                self.cur.close() #close cursor on rollback
            self.cur = None  # Reset the cursor
            self.in_transaction = False
        except Exception as e:
            self.transaction_log.append({
               'timestamp': datetime.now(),
                'operation': 'ROLLBACK',
                'status': 'failed',
                'error': str(e)
            })
            raise e

    def print_log(self):
        for entry in self.transaction_log:
            print(f"\nTimestamp: {entry['timestamp']}")
            if 'query' in entry:
                print(f"Query: {entry['query']}")
            if 'operation' in entry:
                print(f"Operation: {entry['operation']}")
            print(f"Status: {entry['status']}")
            if 'rowcount' in entry:
                print(f"Rows affected: {entry['rowcount']}")
            if 'statusmessage' in entry:
                print(f"Status message: {entry['statusmessage']}")
            if 'error' in entry:
                print(f"Error: {entry['error']}")

    def __enter__(self):
        self.cur = self.conn.cursor()
        if not self.in_transaction:  # Start transaction if not already started
            self.cur.execute("BEGIN")
            self.in_transaction = True
            self.transaction_log.append({
                'timestamp': datetime.now(),
                'operation': 'BEGIN',
                'status': 'success'
            })

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        if self.cur:
            self.cur.close()
        self.cur = None
        self.in_transaction = False
