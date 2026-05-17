# models/user.py

from database.db_manager import DatabaseManager


class User:
    """
    BASE CLASS for all users in the system...
    
    OOP Concept - ABSTRACTION:
    This class defines WHAT a user can do (the interface),
    without implementing every detail here.
    
    OOP Concept - ENCAPSULATION:
    User data is stored in private-like attributes (_password).
    We use methods to interact with data safely.
    """

    def __init__(self, user_id, username, role, full_name, email="", phone=""):
        self.user_id   = user_id
        self.username  = username
        self.role      = role
        self.full_name = full_name
        self.email     = email
        self.phone     = phone
        self._db       = DatabaseManager()  # Each user has database access

    def get_dashboard_title(self):
        """
        OOP Concept - POLYMORPHISM:
        Admin and Member will OVERRIDE this method
        to return different dashboard titles.
        """
        return "SmartFit Dashboard"

    def update_profile(self, full_name, email, phone):
        """Updates user info in the database."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET full_name = ?, email = ?, phone = ?
            WHERE id = ?
        """, (full_name, email, phone, self.user_id))
        conn.commit()
        conn.close()

        # Update local attributes too
        self.full_name = full_name
        self.email     = email
        self.phone     = phone

    def change_password(self, new_password):
        """Hashes and saves a new password."""
        from utils.auth import hash_password
        hashed = hash_password(new_password)

        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET password = ? WHERE id = ?
        """, (hashed, self.user_id))
        conn.commit()
        conn.close()

    def __str__(self):
        """String representation — useful for debugging."""
        return f"{self.role.capitalize()}: {self.full_name} (@{self.username})"

