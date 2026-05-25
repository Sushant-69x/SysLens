import sqlite3
import os
from Utils.logger import get_logger

logger = get_logger('DBManager')

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        with self.get_connection() as conn:
            conn.executescript(schema)
        logger.info("Database schema initialized")

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def insert(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        with self.get_connection() as conn:
            conn.execute(sql, list(data.values()))
            conn.commit()

    def query(self, sql, params=()):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]