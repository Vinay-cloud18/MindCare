import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "journal.db"


def get_connection():
    return sqlite3.connect(DB_PATH, timeout=10)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                entry_text TEXT NOT NULL,
                emotion TEXT,
                sentiment TEXT,
                confidence REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                daily_reminder INTEGER DEFAULT 1,
                reminder_time TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)


def get_user_entries(user_id):
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT date, entry_text, emotion, sentiment, confidence
            FROM entries
            WHERE user_id = ?
            ORDER BY date DESC, id DESC
        """, (user_id,))
        return cursor.fetchall()


def add_user_entry(
    user_id, date, entry_text, emotion, sentiment, confidence
):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO entries (
                user_id, date, entry_text, emotion, sentiment, confidence
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id, date, entry_text, emotion, sentiment, confidence
        ))