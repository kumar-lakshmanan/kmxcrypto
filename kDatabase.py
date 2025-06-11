'''
@name: Simple KDATAbase
@author:  kayma
@createdon: 11-May-2025
@description:



 
'''
__created__ = "11-May-2025" 
__updated__ = "11-May-2025"
__author__ = "kayma"

from typing import List, Tuple, Optional
from urllib.parse import quote
import mysql.connector
import couchdb
import sqlite3

#
# # Connect to CouchDB server
#
#
# # Access a database
# db = couch['my_database']
#
# # Get a document
# doc = db['document_id']
# print(doc)
#
# # Add a new document
# db.save({'type': 'person', 'name': 'Kumar', 'age': 41})


class SimpleCouchDB():

    def __init__(self,database="mydata", dbuser="root",dbpass="pass"):
        host = "localhost"
        port = "5984"
        dbpass = quote(dbpass)
        self.conn = couchdb.Server(f'http://{dbuser}:{dbpass}@{host}:{port}/')
        self.db = self.conn[database]

    def getAllDocuments(self):
        if self.db:
            # Get all documents using _all_docs view
            docs = []
            for row in self.db.view('_all_docs', include_docs=True):
                docs.append(row.doc)  # row.doc is a dict
            return docs
        return []

    def getDocument(self,doc_id):
        if self.db:
            return self.db[doc_id]
        return None

    def setDocument(self, data={}):
        if data and self.db:
            self.db.save(data)
            return 1
        return 0

class SimpleMySql:
    
    def __init__(self,dbuser="root",dbpass="pas"):
        self.conn = None
        self.dbuser = dbuser
        self.dbpass = dbpass

    def connect(self):
        if self.conn is None:        
            self.conn = mysql.connector.connect(
                            host="127.0.0.1",
                            port=3306,
                            user=self.dbuser,
                            password=self.dbpass)
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
    def __init__(self, db_path):
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