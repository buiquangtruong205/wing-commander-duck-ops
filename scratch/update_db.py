import sqlite3
import os

db_path = "e:/Computer_Vision/wing-commander-duck-ops/duck_ops.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE PlayerSetting SET flip_camera = 0")
    conn.commit()
    print(f"Updated {cursor.rowcount} users' flip_camera setting to 0.")
    conn.close()
else:
    print("Database not found.")
