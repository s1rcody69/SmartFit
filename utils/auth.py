import hashlib
import sqlite3
from database.db_manager import DatabaseManager


# Converts password into a hashstring
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Checks username and password against the database, returns dict with user info(if login is sucessful)
def verify_login(username: str, password: str):
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()

    hashed = hash_password(password)

    cursor.execute("""
        SELECT id, username, role, full_name, email, phone
        FROM users
        WHERE username = ? AND password = ?
    """, (username, hashed))

    user = cursor.fetchone()
    conn.close()

# Convert Row object to a regular dictionary
    if user:
       return dict(user) 
    return None


