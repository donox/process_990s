import psycopg2
from datetime import datetime
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
                    result = independent_cur.fetchall() if independent_cur.description else None
                    independent_conn.commit()
                    return result
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
