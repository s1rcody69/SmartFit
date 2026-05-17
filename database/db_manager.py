import sqlite3
import os

# The database file will be created in the SmartFit/ root folder
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),"smartfit.db")

# Handles all the database connection ad setup
class DatabaseManager:
    
# This line of code initializes the object by storing the database's file location and immediately ensuring all necessary tables are built and ready for use.
    def __init__(self):
        self.db_path = DB_PATH
        self.create_tables()

# Returns a connection to the sqlite database
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
    # lets me access colums by name
        conn.row_factory = sqlite3.Row 
        return conn

# Creates all tables if they don't already exsist
    def create_tables(self):
       conn = self.get_connection()
       cursor = conn.cursor()
# USERS TABLE 
# Stores both admins and members (role tells them apart)
       cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    UNIQUE NOT NULL,
                password    TEXT    NOT NULL,
                role        TEXT    NOT NULL CHECK(role IN ('admin', 'member')),
                full_name   TEXT    NOT NULL,
                email       TEXT,
                phone       TEXT,
                created_at  TEXT    DEFAULT (datetime('now'))
            )
        """)

#  MEMBERS TABLE 
# Extra details specific to members (links to users table)
       cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER UNIQUE NOT NULL,
                date_of_birth   TEXT,
                gender          TEXT,
                address         TEXT,
                emergency_contact TEXT,
                join_date       TEXT    DEFAULT (date('now')),
                membership_plan TEXT    DEFAULT 'Basic',
                membership_start TEXT,
                membership_end  TEXT,
                status          TEXT    DEFAULT 'Active',
                trainer_id      INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

#  TRAINERS TABLE 
       cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainers (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name    TEXT    NOT NULL,
                email        TEXT,
                phone        TEXT,
                specialty    TEXT,
                hire_date    TEXT    DEFAULT (date('now')),
                status       TEXT    DEFAULT 'Active'
            )
        """)

#MEMBERSHIP PLANS TABLE 
       cursor.execute("""
            CREATE TABLE IF NOT EXISTS membership_plans (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_name    TEXT    UNIQUE NOT NULL,
                duration_months INTEGER NOT NULL,
                price        REAL    NOT NULL,
                description  TEXT
            )
        """)

# PAYMENTS TABLE 
       cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id    INTEGER NOT NULL,
                amount       REAL    NOT NULL,
                plan_name    TEXT,
                payment_date TEXT    DEFAULT (date('now')),
                payment_method TEXT  DEFAULT 'Cash',
                status       TEXT    DEFAULT 'Paid',
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)

#  ATTENDANCE TABLE 
       cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id    INTEGER NOT NULL,
                check_in     TEXT    DEFAULT (datetime('now')),
                check_out    TEXT,
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)

#  WORKOUT PLANS TABLE 
       cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_plans (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id    INTEGER NOT NULL,
                plan_name    TEXT    NOT NULL,
                exercises    TEXT,
                assigned_by  INTEGER,
                created_at   TEXT    DEFAULT (date('now')),
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)

# FITNESS PROGRESS TABLE 
       cursor.execute("""
            CREATE TABLE IF NOT EXISTS fitness_progress (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id    INTEGER NOT NULL,
                weight_kg    REAL,
                height_cm    REAL,
                bmi          REAL,
                notes        TEXT,
                recorded_at  TEXT    DEFAULT (date('now')),
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)

       conn.commit()
       conn.close()
       print("Database set up complete")
    
# inserts default admin account and membership plans
    def seed_default_data(self):
        """
        Inserts default admin account and membership plans
        so the app works right away on first launch.
        """
        from utils.auth import hash_password

        conn = self.get_connection()
        cursor = conn.cursor()

# Create default admin if none exists
        cursor.execute("SELECT * FROM users WHERE role = 'admin'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (username, password, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "admin",
                hash_password("admin123"),
                "admin",
                "System Administrator",
                "admin@smartfit.com"
            ))
            print("Default admin created → username: admin | password: admin123")

 #Create default membership plans if none exist 
        cursor.execute("SELECT COUNT(*) FROM membership_plans")
        count = cursor.fetchone()[0]
        if count == 0:
            plans = [
                ("Basic",    1, 1500,  "Access to gym floor and basic equipment"),
                ("Standard", 3, 4000,  "Basic + group classes"),
                ("Premium",  6, 7000,  "Standard + personal trainer sessions"),
                ("VIP",      12, 12000, "Full access to all facilities and services"),
            ]
            cursor.executemany("""
                INSERT INTO membership_plans (plan_name, duration_months, price, description)
                VALUES (?, ?, ?, ?)
            """, plans)
            print("Default membership plans created.")

        conn.commit()
        conn.close()

