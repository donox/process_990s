import psycopg2
from typing import List, Any, Optional
from datetime import datetime


class DBTransaction:
    """Manage DB transactions in a single place."""
    def __init__(self, conn):
        self.conn = conn
        self.cur = conn.cursor()
        self.transaction_log = []

    def execute(self, query: str, params: tuple = None) -> Optional[List[tuple]]:
        """Execute a query with parameters, log it, and handle any errors"""
        try:
            # Log the operation with timestamp
            actual_query = self.cur.mogrify(query, params).decode('utf-8')
            self.transaction_log.append({
                'timestamp': datetime.now(),
                'query': actual_query,
                'status': 'pending'
            })

            # Execute the query
            self.cur.execute(query, params)

            # Update log with success
            self.transaction_log[-1]['status'] = 'success'
            self.transaction_log[-1]['rowcount'] = self.cur.rowcount
            self.transaction_log[-1]['statusmessage'] = self.cur.statusmessage

            # Return results if it's a SELECT
            if query.strip().upper().startswith('SELECT'):
                return self.cur.fetchall()
            return None

        except Exception as e:
            # Update log with failure
            self.transaction_log[-1]['status'] = 'failed'
            self.transaction_log[-1]['error'] = str(e)
            raise

    def commit(self):
        """Commit the transaction"""
        try:
            self.conn.commit()
            self.transaction_log.append({
                'timestamp': datetime.now(),
                'operation': 'COMMIT',
                'status': 'success'
            })
        except Exception as e:
            self.transaction_log.append({
                'timestamp': datetime.now(),
                'operation': 'COMMIT',
                'status': 'failed',
                'error': str(e)
            })
            raise

    def rollback(self):
        """Rollback the transaction"""
        try:
            self.conn.rollback()
            self.transaction_log.append({
                'timestamp': datetime.now(),
                'operation': 'ROLLBACK',
                'status': 'success'
            })
        except Exception as e:
            self.transaction_log.append({
                'timestamp': datetime.now(),
                'operation': 'ROLLBACK',
                'status': 'failed',
                'error': str(e)
            })
            raise

    def print_log(self):
        """Print the transaction log"""
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
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure proper cleanup when used in 'with' statement"""
        if exc_type is not None:
            self.rollback()
        self.cur.close()