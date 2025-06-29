import sqlite3
import logging
from typing import Set


class Database:
    """
    Database handler for bot settings and user management.
    Implements SQLite storage for persistent data.
    """

    def __init__(self, db_path: str = "bot_data.db"):
        """
        Initialize database connection and create required tables.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        logging.info(f"Initializing database at {db_path}")
        self._init_db()

    def _init_db(self):
        """Initialize database tables and default settings."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create tables
                logging.info("Creating database tables if they don't exist")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value INTEGER
                    )
                """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        authorized INTEGER DEFAULT 0
                    )
                """
                )

                # Insert default settings
                default_settings = [
                    ("auto_transcription_enabled", 1),
                    ("enhanced_transcription_enabled", 0),
                    ("output_text_file_enabled", 0),
                    ("auto_summarize_enabled", 0),
                    ("transcription_speed", 1),
                ]

                logging.info("Inserting default settings")
                cursor.executemany(
                    """
                    INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
                """,
                    default_settings,
                )

                conn.commit()
                logging.info("Database initialized successfully")

        except Exception as e:
            logging.error(f"Database initialization failed: {str(e)}", exc_info=True)
            raise

    def get_setting(self, key: str) -> bool:
        """
        Get boolean setting value from database.

        Args:
            key: Setting key to retrieve

        Returns:
            bool: Setting value
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                result = cursor.fetchone()
                value = bool(result[0]) if result else False
                logging.info(f"Retrieved setting {key}={value}")
                return value
        except Exception as e:
            logging.error(f"Error getting setting {key}: {str(e)}")
            return False

    def get_int_setting(self, key: str) -> int:
        """
        Get integer setting value from database.

        Args:
            key: Setting key to retrieve

        Returns:
            int: Setting value
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                result = cursor.fetchone()
                value = int(result[0]) if result else 1
                logging.info(f"Retrieved int setting {key}={value}")
                return value
        except Exception as e:
            logging.error(f"Error getting int setting {key}: {str(e)}")
            return 1

    def set_setting(self, key: str, value: bool):
        """
        Set boolean setting value in database.

        Args:
            key: Setting key to update
            value: New boolean value
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
                """,
                    (key, int(value)),
                )
                conn.commit()
                logging.info(f"Updated setting {key}={value}")
        except Exception as e:
            logging.error(f"Error setting {key}={value}: {str(e)}")
            raise

    def set_int_setting(self, key: str, value: int):
        """
        Set integer setting value in database.

        Args:
            key: Setting key to update
            value: New integer value
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
                """,
                    (key, value),
                )
                conn.commit()
                logging.info(f"Updated int setting {key}={value}")
        except Exception as e:
            logging.error(f"Error setting int {key}={value}: {str(e)}")
            raise

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
                cursor.execute("SELECT user_id FROM users WHERE authorized = 1")
                return {row[0] for row in cursor.fetchall()}
        except Exception as e:
            logging.error(f"Error getting authorized users: {e}")
            return set()

    def add_authorized_user(self, user_id: str):
        """Add a user ID to the authorized users list."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO users (user_id, authorized) VALUES (?, 1)
                """,
                    (user_id,),
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Error adding authorized user {user_id}: {e}")

    def add_user(self, user_id: str):
        """Add a user ID to the users list."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO users (user_id) VALUES (?)
                """,
                    (user_id,),
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Error adding user {user_id}: {e}")

    def is_user_registered(self, user_id: str) -> bool:
        """Check if a user is registered."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"Error checking if user {user_id} is registered: {e}")
            return False

    def is_user_authorized(self, user_id: str) -> bool:
        """Check if a user is authorized."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT authorized FROM users WHERE user_id = ?", (user_id,)
                )
                result = cursor.fetchone()
                return result[0] == 1 if result else False
        except Exception as e:
            logging.error(f"Error checking if user {user_id} is authorized: {e}")
            return False


# Create a global instance of Database
db = Database()
