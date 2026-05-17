from models.user import User


class Member(User):
    """
    MEMBER user — inherits from User.
    Has access to their own data only.
    
    OOP Concept - ENCAPSULATION:
    Members can only read/write THEIR OWN data.
    The methods enforce this by always filtering by self.user_id.
    """

    def __init__(self, user_id, username, full_name, email="", phone=""):
        super().__init__(user_id, username, "member", full_name, email, phone)
        self.member_id = None  # Will be loaded by load_member_profile()
        self.load_member_profile()

    def get_dashboard_title(self):
        """POLYMORPHISM — overrides the parent method."""
        return f"SmartFit — Welcome, {self.full_name.split()[0]}!"

    def load_member_profile(self):
        """Loads the extended member profile from the database."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM members WHERE user_id = ?
        """, (self.user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            data = dict(row)
            self.member_id        = data.get("id")
            self.date_of_birth    = data.get("date_of_birth", "")
            self.gender           = data.get("gender", "")
            self.address          = data.get("address", "")
            self.membership_plan  = data.get("membership_plan", "Basic")
            self.membership_start = data.get("membership_start", "")
            self.membership_end   = data.get("membership_end", "")
            self.status           = data.get("status", "Active")

    def get_attendance_history(self):
        """Returns this member's last 30 attendance records."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT check_in, check_out FROM attendance
            WHERE member_id = ?
            ORDER BY check_in DESC
            LIMIT 30
        """, (self.member_id,))
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records

    def check_in(self):
        """Records a gym check-in for today."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attendance (member_id) VALUES (?)
        """, (self.member_id,))
        conn.commit()
        conn.close()

    def get_workout_plan(self):
        """Returns the most recent workout plan assigned to this member."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM workout_plans
            WHERE member_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (self.member_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_progress_records(self):
        """Returns all fitness progress entries for this member."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM fitness_progress
            WHERE member_id = ?
            ORDER BY recorded_at DESC
        """, (self.member_id,))
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records

    def add_progress_entry(self, weight_kg, height_cm, notes=""):
        """Saves a new fitness progress entry and calculates BMI."""
        bmi = round(weight_kg / ((height_cm / 100) ** 2), 2)
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fitness_progress (member_id, weight_kg, height_cm, bmi, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (self.member_id, weight_kg, height_cm, bmi, notes))
        conn.commit()
        conn.close()
        return bmi
