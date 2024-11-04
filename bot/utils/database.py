import sqlite3
import logging
from typing import Set

class Database:
    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Create settings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value INTEGER
                    )
                """)

                # Create authorized users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS authorized_users (
                        user_id TEXT PRIMARY KEY
                    )
                """)

                # Insert default settings if they don't exist
                default_settings = [
                    ('auto_transcription_enabled', 1),
                    ('enhanced_transcription_enabled', 0),
                    ('output_text_file_enabled', 0),
                    ('auto_summarize_enabled', 0)
                ]

                cursor.executemany("""
                    INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
                """, default_settings)

                conn.commit()
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    def get_setting(self, key: str) -> bool:
        """Get a boolean setting value from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                result = cursor.fetchone()
                return bool(result[0]) if result else False
        except Exception as e:
            logging.error(f"Error getting setting {key}: {e}")
            return False

    def set_setting(self, key: str, value: bool):
        """Set a boolean setting value in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
                """, (key, int(value)))
                conn.commit()
        except Exception as e:
            logging.error(f"Error setting {key} to {value}: {e}")

    def toggle_setting(self, key: str) -> bool:
        """Toggle a boolean setting and return its new value."""
        try:
            current_value = self.get_setting(key)
            new_value = not current_value
            self.set_setting(key, new_value)
            return new_value
        except Exception as e:
            logging.error(f"Error toggling setting {key}: {e}")
            return False

    def get_authorized_users(self) -> Set[str]:
        """Get the set of authorized user IDs."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM authorized_users")
                return {row[0] for row in cursor.fetchall()}
        except Exception as e:
            logging.error(f"Error getting authorized users: {e}")
            return set()

    def add_authorized_user(self, user_id: str):
        """Add a user ID to the authorized users list."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO authorized_users (user_id) VALUES (?)
                """, (user_id,))
                conn.commit()
        except Exception as e:
            logging.error(f"Error adding authorized user {user_id}: {e}")

# Create a global instance of Database
db = Database() 