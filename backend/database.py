import os
import sqlite3
from typing import Optional

import mysql.connector
from mysql.connector import Error

DB_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(DB_DIR, "career_guidance.db")
MYSQL_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "career_guidance"),
    "autocommit": False,
}


def get_db_backend() -> str:
    return "sqlite" if os.environ.get("USE_SQLITE", "1") == "1" else "mysql"


def _ensure_sqlite_schema(connection: sqlite3.Connection):
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            education TEXT,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS assessment_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            realistic_score INTEGER NOT NULL,
            investigative_score INTEGER NOT NULL,
            artistic_score INTEGER NOT NULL,
            social_score INTEGER NOT NULL,
            enterprising_score INTEGER NOT NULL,
            conventional_score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS course_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            riasec_type TEXT NOT NULL,
            category_name TEXT NOT NULL,
            category_description TEXT NOT NULL,
            name TEXT NOT NULL,
            icon TEXT NOT NULL,
            level TEXT NOT NULL,
            duration TEXT NOT NULL,
            description TEXT NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0,
            UNIQUE(riasec_type, name)
        );

        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    connection.commit()


class SQLiteCursorWrapper:
    def __init__(self, cursor, dictionary=False):
        self._cursor = cursor
        self._dictionary = dictionary

    @staticmethod
    def _normalize_query(query):
        return query.replace("%s", "?")

    def execute(self, query, params=()):
        return self._cursor.execute(self._normalize_query(query), params)

    def executemany(self, query, seq_of_params):
        return self._cursor.executemany(self._normalize_query(query), seq_of_params)

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if self._dictionary:
            return dict(row)
        return row

    def fetchall(self):
        rows = self._cursor.fetchall()
        if self._dictionary:
            return [dict(row) for row in rows]
        return rows

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    def close(self):
        self._cursor.close()

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class SQLiteConnectionWrapper:
    def __init__(self):
        self._connection = sqlite3.connect(SQLITE_DB_PATH)
        self._connection.row_factory = sqlite3.Row
        _ensure_sqlite_schema(self._connection)

    def cursor(self, dictionary=False):
        cursor = self._connection.cursor()
        return SQLiteCursorWrapper(cursor, dictionary=dictionary)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()

    def is_connected(self):
        return True


def get_db_connection():
    backend = get_db_backend()

    if backend == "mysql":
        try:
            connection = mysql.connector.connect(**MYSQL_CONFIG)
            if connection.is_connected():
                print("MySQL Connected Successfully!")
                return connection
        except Error as e:
            print("MySQL connection error:", e)

    try:
        sqlite_connection = SQLiteConnectionWrapper()
        print("SQLite Connected Successfully!")
        return sqlite_connection
    except Exception as e:
        print("SQLite connection error:", e)
        return None