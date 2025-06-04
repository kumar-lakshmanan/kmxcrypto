'''
@name: Simple KDATAbase
@author:  kayma
@createdon: 11-May-2025
@description:



 
'''
__created__ = "11-May-2025" 
__updated__ = "11-May-2025"
__author__ = "kayma"

import sqlite3
from typing import List, Tuple, Optional
import mysql.connector
from common_lib import kTools

class SimpleMySql:    
    def __init__(self):
        self.conn = None
        self.tls = kTools.KTools()
        
    def connect(self):
        
        if self.conn is None:
            connection_name = "kaymatrix:us-central1:mycryptodb"
            db_name = "kmxcryptos"
            db_user = "root"
            db_password = self.tls.getEnv('DB_PASS', None)
            is_prod = self.tls.getEnv('IS_PROD', 0)
            socket_path = f"/cloudsql/{connection_name}"
            if is_prod:
                self.conn = mysql.connector.connect(
                    user=db_user,
                    password=db_password,
                    unix_socket=socket_path,
                    database=db_name
                )
            else:
                self.conn = mysql.connector.connect(
                    user=db_user,
                    password=db_password,
                    host="127.0.0.1",
                    port=3306,
                    database=db_name
                )
        return self.conn

    def execute_query(self, query: str, params: Tuple = ()) -> None:
        """Execute INSERT/UPDATE/DELETE queries."""
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        self.cursor.execute(query, params)

    def commit_all(self):
        if self.conn: self.conn.commit()
        
    def fetch_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute SELECT query and return results as list of tuples."""
        self.conn = self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()        

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

class SimpleSQLite:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def execute_query(self, query: str, params: Tuple = ()) -> None:
        """Execute INSERT/UPDATE/DELETE queries."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

    def fetch_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute SELECT query and return results as list of tuples."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def list_tables(self) -> List[str]:
        """Return a list of table names in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        results = self.fetch_query(query)
        return [row[0] for row in results]

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


if __name__ == '__main__':
    dbname = ""
    db = SimpleSQLite("test.db")
    
    # Add or update
    db.execute_query("INSERT INTO users (name, age) VALUES (?, ?)", ("Alice", 30))
    
    # Fetch
    results = db.fetch_query("SELECT * FROM users WHERE age > ?", (25,))
    print(results)  # List of tuples
    
    # List tables
    tables = db.list_tables()
    print(tables)
    
    # Close when done
    db.close()    