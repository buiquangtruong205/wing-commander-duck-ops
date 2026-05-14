import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="duck_ops.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # PlayerProfile Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS PlayerProfile (
                    username TEXT PRIMARY KEY,
                    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # HighScores Table (HighSrose in image)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS HighScores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    difficulty TEXT,
                    highest_score INTEGER,
                    achieved_date TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES PlayerProfile (username)
                )
            """)
            
            # PlayerSetting Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS PlayerSetting (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    music_volume REAL DEFAULT 0.5,
                    sfx_volume REAL DEFAULT 0.5,
                    is_fullscreen BOOLEAN DEFAULT 0,
                    camera_index INTEGER DEFAULT 0,
                    flip_camera BOOLEAN DEFAULT 1,
                    tracking_sensitivity REAL DEFAULT 1.0,
                    FOREIGN KEY (username) REFERENCES PlayerProfile (username)
                )
            """)
            
            # Meta Table for persistence
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Meta (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def login_player(self, username):
        """Checks if player exists, if not creates new profile and settings."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM PlayerProfile WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if not result:
                # Create profile
                cursor.execute("INSERT INTO PlayerProfile (username) VALUES (?)", (username,))
                # Create default settings
                cursor.execute("INSERT INTO PlayerSetting (username) VALUES (?)", (username,))
                conn.commit()
                return True, "New profile created."
            return True, "Welcome back."

    def get_player_settings(self, username):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PlayerSetting WHERE username = ?", (username,))
            return dict(cursor.fetchone())

    def update_settings(self, username, settings_dict):
        # settings_dict keys should match column names
        cols = ", ".join([f"{k} = ?" for k in settings_dict.keys()])
        params = list(settings_dict.values()) + [username]
        with self.get_connection() as conn:
            conn.execute(f"UPDATE PlayerSetting SET {cols} WHERE username = ?", params)
            conn.commit()

    def add_high_score(self, username, score, difficulty):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check if current score is higher than existing
            cursor.execute("""
                SELECT highest_score FROM HighScores 
                WHERE username = ? AND difficulty = ?
            """, (username, difficulty))
            row = cursor.fetchone()
            
            if not row or score > row[0]:
                if not row:
                    cursor.execute("""
                        INSERT INTO HighScores (username, difficulty, highest_score, achieved_date)
                        VALUES (?, ?, ?, ?)
                    """, (username, difficulty, score, now))
                else:
                    cursor.execute("""
                        UPDATE HighScores SET highest_score = ?, achieved_date = ?
                        WHERE username = ? AND difficulty = ?
                    """, (score, now, username, difficulty))
                conn.commit()

    def get_leaderboard(self, limit=10):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, difficulty, highest_score, achieved_date
                FROM HighScores 
                ORDER BY difficulty ASC, highest_score DESC, achieved_date DESC
                LIMIT ?
            """, (limit,))
            return [
                {
                    "name": row[0],
                    "mode": row[1],
                    "score": row[2],
                    "date": row[3],
                }
                for row in cursor.fetchall()
            ]

    def get_last_user(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM Meta WHERE key = 'last_user'")
            result = cursor.fetchone()
            return result[0] if result else None

    def set_last_user(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO Meta (key, value) VALUES ('last_user', ?)", (username,))
            conn.commit()
