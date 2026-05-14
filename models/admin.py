import sqlite3
from models.user import User
from database.db_manager import DatabaseManager



class Admin(User):
    """
    ADMIN user — inherits everything from User...
    
    OOP Concept - INHERITANCE:
    Admin gets all User methods for free, plus
    its own admin-specific methods below.
    """

    def __init__(self, user_id, username, full_name, email="", phone=""):
        # Call the parent class constructor
        super().__init__(user_id, username, "admin", full_name, email, phone)

    def get_dashboard_title(self):
        """POLYMORPHISM — overrides the parent method."""
        return "SmartFit — Admin Dashboard"

    # ── Member Management ──────────────────────────────────────────

    def get_all_members(self):
        """Returns all members with their user info joined."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, u.email, u.phone,
                   m.id as member_id, m.membership_plan, m.status,
                   m.membership_end, m.join_date
            FROM users u
            JOIN members m ON u.id = m.user_id
            WHERE u.role = 'member'
            ORDER BY u.full_name
        """)
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return members

    def add_member(self, username, password, full_name, email, phone,
                   plan, membership_start, membership_end):
        """Creates a new member user and member record."""
        from utils.auth import hash_password
        conn = self._db.get_connection()
        cursor = conn.cursor()
        try:
            # Step 1: Create the user account
            cursor.execute("""
                INSERT INTO users (username, password, role, full_name, email, phone)
                VALUES (?, ?, 'member', ?, ?, ?)
            """, (username, hash_password(password), full_name, email, phone))

            user_id = cursor.lastrowid  # Get the new user's ID

            # Step 2: Create the member profile
            cursor.execute("""
                INSERT INTO members (user_id, membership_plan, membership_start,
                                     membership_end, status)
                VALUES (?, ?, ?, ?, 'Active')
            """, (user_id, plan, membership_start, membership_end))

            conn.commit()
            return True, "Member added successfully!"
        except sqlite3.IntegrityError:
            return False, "Username already exists."
        finally:
            conn.close()

    def delete_member(self, user_id):
        """Deletes a member from the system."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM members WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

    def search_members(self, keyword):
        """Searches members by name, username, or email."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        like = f"%{keyword}%"
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, u.email, u.phone,
                   m.id as member_id, m.membership_plan, m.status,
                   m.membership_end, m.join_date
            FROM users u
            JOIN members m ON u.id = m.user_id
            WHERE u.role = 'member'
              AND (u.full_name LIKE ? OR u.username LIKE ? OR u.email LIKE ?)
            ORDER BY u.full_name
        """, (like, like, like))
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return members

    # ── Trainer Management ────────────────────────────────────────

    def get_all_trainers(self):
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trainers ORDER BY full_name")
        trainers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return trainers

    def add_trainer(self, full_name, email, phone, specialty):
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trainers (full_name, email, phone, specialty)
            VALUES (?, ?, ?, ?)
        """, (full_name, email, phone, specialty))
        conn.commit()
        conn.close()

    # ── Payments ──────────────────────────────────────────────────

    def get_all_payments(self):
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, u.full_name, p.amount, p.plan_name,
                   p.payment_date, p.payment_method, p.status
            FROM payments p
            JOIN members m ON p.member_id = m.id
            JOIN users u ON m.user_id = u.id
            ORDER BY p.payment_date DESC
        """)
        payments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return payments

    def add_payment(self, member_id, amount, plan_name, method):
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payments (member_id, amount, plan_name, payment_method)
            VALUES (?, ?, ?, ?)
        """, (member_id, amount, plan_name, method))
        conn.commit()
        conn.close()

    # ── Attendance ────────────────────────────────────────────────

    def get_all_attendance(self):
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, u.full_name, a.check_in, a.check_out
            FROM attendance a
            JOIN members m ON a.member_id = m.id
            JOIN users u ON m.user_id = u.id
            ORDER BY a.check_in DESC
            LIMIT 100
        """)
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records

    # ── Plans ─────────────────────────────────────────────────────

    def get_all_plans(self):
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM membership_plans ORDER BY price")
        plans = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return plans

    def get_dashboard_stats(self):
        """Returns quick stats for the admin dashboard overview."""
        conn = self._db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM members WHERE status='Active'")
        active_members = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM trainers WHERE status='Active'")
        active_trainers = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM payments
            WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
        """)
        monthly_revenue = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM attendance
            WHERE date(check_in) = date('now')
        """)
        today_attendance = cursor.fetchone()[0]

        conn.close()
        return {
            "active_members":  active_members,
            "active_trainers": active_trainers,
            "monthly_revenue": monthly_revenue,
            "today_attendance": today_attendance,
        }