
import tkinter as tk
from tkinter import messagebox
from utils.auth import verify_login
from datetime import date

BG_COLOR      = "#1a1a2e"
CARD_COLOR    = "#16213e"
ACCENT_COLOR  = "#e94560"
TEXT_COLOR    = "#eaeaea"
SUBTEXT_COLOR = "#a0a0b0"
INPUT_BG      = "#0f3460"
BTN_COLOR     = "#e94560"
BTN_HOVER     = "#c73652"
TAB_ACTIVE    = "#e94560"
TAB_INACTIVE  = "#0f3460"


class LoginScreen:
    """
    Login screen with two tabs — Login and Register.
    Members can self-register. Admins are created by the system only.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("SmartFit Gym System")
        self.root.geometry("500x850")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        self.center_window(500, 850)
        self.build_ui()

    def center_window(self, width, height):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - width)  // 2
        y  = (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def build_ui(self):

        # ── Header ────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=BG_COLOR)
        header.pack(pady=(36, 0))

        tk.Label(
            header, text="",
            font=("Arial", 44),
            bg=BG_COLOR, fg=ACCENT_COLOR
        ).pack()

        tk.Label(
            header, text="SmartFit",
            font=("Arial", 26, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR
        ).pack()

        tk.Label(
            header, text="Gym Management System",
            font=("Arial", 10),
            bg=BG_COLOR, fg=SUBTEXT_COLOR
        ).pack()

        # ── Tab Switcher ──────────────────────────────────────────
        tab_bar = tk.Frame(self.root, bg=BG_COLOR)
        tab_bar.pack(fill="x", padx=40, pady=(20, 0))

        self.login_tab_btn = tk.Button(
            tab_bar, text="Login",
            font=("Arial", 11, "bold"),
            bg=TAB_ACTIVE, fg="white",
            relief="flat", cursor="hand2",
            command=self.show_login_tab
        )
        self.login_tab_btn.pack(side="left", expand=True, fill="x", ipady=8)

        self.register_tab_btn = tk.Button(
            tab_bar, text="Register",
            font=("Arial", 11, "bold"),
            bg=TAB_INACTIVE, fg=SUBTEXT_COLOR,
            relief="flat", cursor="hand2",
            command=self.show_register_tab
        )
        self.register_tab_btn.pack(side="left", expand=True, fill="x", ipady=8)

        # ── Card container ────────────────────────────────────────
        self.card = tk.Frame(self.root, bg=CARD_COLOR, padx=36, pady=24)
        self.card.pack(padx=40, pady=10, fill="both", expand=True)

        # ── Footer hint ───────────────────────────────────────────
        tk.Label(
            self.root,
            text="Admin login: username: admin  |  password: admin123",
            font=("Arial", 8),
            bg=BG_COLOR, fg=SUBTEXT_COLOR
        ).pack(pady=(0, 10))

        # Show login tab by default
        self.show_login_tab()

    # ── Tab Switching ─────────────────────────────────────────────

    def show_login_tab(self):
        """Switches to the Login tab."""
        self.login_tab_btn.config(bg=TAB_ACTIVE, fg="white")
        self.register_tab_btn.config(bg=TAB_INACTIVE, fg=SUBTEXT_COLOR)
        self.clear_card()
        self.build_login_form()

    def show_register_tab(self):
        """Switches to the Register tab."""
        self.register_tab_btn.config(bg=TAB_ACTIVE, fg="white")
        self.login_tab_btn.config(bg=TAB_INACTIVE, fg=SUBTEXT_COLOR)
        self.clear_card()
        self.build_register_form()

    def clear_card(self):
        """Clears the card frame before switching tabs."""
        for widget in self.card.winfo_children():
            widget.destroy()

    # ── Login Form ────────────────────────────────────────────────

    def build_login_form(self):
        tk.Label(
            self.card, text="Welcome Back",
            font=("Arial", 14, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self.card, text="Sign in to your account",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w", pady=(0, 18))

        # Username
        self._label("Username")
        self.login_username = self._entry()

        # Password
        self._label("Password")
        self.login_password = self._entry(show="●")

        # Show password toggle
        self.show_pw_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.card, text="Show password",
            variable=self.show_pw_var,
            command=lambda: self.login_password.config(
                show="" if self.show_pw_var.get() else "●"
            ),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR,
            selectcolor=CARD_COLOR,
            activebackground=CARD_COLOR,
            font=("Arial", 9)
        ).pack(anchor="w", pady=(0, 18))

        # Login button
        btn = tk.Button(
            self.card, text="LOGIN",
            font=("Arial", 12, "bold"),
            bg=BTN_COLOR, fg="white",
            relief="flat", cursor="hand2",
            command=self.attempt_login
        )
        btn.pack(fill="x", ipady=10)
        btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BTN_COLOR))

        # Error message
        self.login_error = tk.Label(
            self.card, text="",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=ACCENT_COLOR
        )
        self.login_error.pack(pady=(10, 0))

        # Switch hint
        tk.Label(
            self.card,
            text="Don't have an account?",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(pady=(14, 0))

        tk.Button(
            self.card, text="Create one here →",
            font=("Arial", 9, "underline"),
            bg=CARD_COLOR, fg=ACCENT_COLOR,
            relief="flat", cursor="hand2",
            activebackground=CARD_COLOR,
            activeforeground=BTN_HOVER,
            command=self.show_register_tab
        ).pack()

        self.root.bind("<Return>", lambda e: self.attempt_login())

    # ── Register Form ─────────────────────────────────────────────

    def build_register_form(self):
        tk.Label(
            self.card, text="Create Account",
            font=("Arial", 14, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self.card, text="Register as a new gym member",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w", pady=(0, 14))

        # Two-column layout for compact fields
        row1 = tk.Frame(self.card, bg=CARD_COLOR)
        row1.pack(fill="x", pady=(0, 2))

        # Full Name
        left = tk.Frame(row1, bg=CARD_COLOR)
        left.pack(side="left", expand=True, fill="x", padx=(0, 6))
        tk.Label(left, text="Full Name", font=("Arial", 9),
                 bg=CARD_COLOR, fg=SUBTEXT_COLOR).pack(anchor="w")
        self.reg_name = self._entry(parent=left)

        # Phone
        right = tk.Frame(row1, bg=CARD_COLOR)
        right.pack(side="left", expand=True, fill="x")
        tk.Label(right, text="Phone", font=("Arial", 9),
                 bg=CARD_COLOR, fg=SUBTEXT_COLOR).pack(anchor="w")
        self.reg_phone = self._entry(parent=right)

        # Email
        self._label("Email")
        self.reg_email = self._entry()

        # Username
        self._label("Username")
        self.reg_username = self._entry()

        # Two-column for passwords
        row2 = tk.Frame(self.card, bg=CARD_COLOR)
        row2.pack(fill="x", pady=(0, 2))

        left2 = tk.Frame(row2, bg=CARD_COLOR)
        left2.pack(side="left", expand=True, fill="x", padx=(0, 6))
        tk.Label(left2, text="Password", font=("Arial", 9),
                 bg=CARD_COLOR, fg=SUBTEXT_COLOR).pack(anchor="w")
        self.reg_password = self._entry(parent=left2, show="●")

        right2 = tk.Frame(row2, bg=CARD_COLOR)
        right2.pack(side="left", expand=True, fill="x")
        tk.Label(right2, text="Confirm Password", font=("Arial", 9),
                 bg=CARD_COLOR, fg=SUBTEXT_COLOR).pack(anchor="w")
        self.reg_confirm = self._entry(parent=right2, show="●")

        # Register button
        btn = tk.Button(
            self.card, text="CREATE ACCOUNT",
            font=("Arial", 12, "bold"),
            bg=BTN_COLOR, fg="white",
            relief="flat", cursor="hand2",
            command=self.attempt_register
        )
        btn.pack(fill="x", ipady=10, pady=(12, 0))
        btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BTN_COLOR))

        # Error / success message
        self.reg_msg = tk.Label(
            self.card, text="",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=ACCENT_COLOR,
            wraplength=380
        )
        self.reg_msg.pack(pady=(8, 0))

        # Switch hint
        tk.Label(
            self.card, text="Already have an account?",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(pady=(10, 0))

        tk.Button(
            self.card, text="Sign in here →",
            font=("Arial", 9, "underline"),
            bg=CARD_COLOR, fg=ACCENT_COLOR,
            relief="flat", cursor="hand2",
            activebackground=CARD_COLOR,
            activeforeground=BTN_HOVER,
            command=self.show_login_tab
        ).pack()

    # ── Auth Logic ────────────────────────────────────────────────

    def attempt_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        if not username or not password:
            self.login_error.config(text="⚠ Please enter username and password.")
            return

        user_data = verify_login(username, password)

        if user_data is None:
            self.login_error.config(text="✗ Invalid username or password.")
            return

        self.open_dashboard(user_data)

    def attempt_register(self):
        """Validates and creates a new member account."""
        full_name = self.reg_name.get().strip()
        phone     = self.reg_phone.get().strip()
        email     = self.reg_email.get().strip()
        username  = self.reg_username.get().strip()
        password  = self.reg_password.get().strip()
        confirm   = self.reg_confirm.get().strip()

        # ── Validation ────────────────────────────────────────────
        if not full_name or not username or not password:
            self.reg_msg.config(
                fg=ACCENT_COLOR,
                text="⚠ Full name, username and password are required."
            )
            return

        if len(username) < 3:
            self.reg_msg.config(
                fg=ACCENT_COLOR,
                text="⚠ Username must be at least 3 characters."
            )
            return

        if len(password) < 6:
            self.reg_msg.config(
                fg=ACCENT_COLOR,
                text="⚠ Password must be at least 6 characters."
            )
            return

        if password != confirm:
            self.reg_msg.config(
                fg=ACCENT_COLOR,
                text="⚠ Passwords do not match."
            )
            return

        # ── Save to database ──────────────────────────────────────
        from utils.auth import hash_password
        from database.db_manager import DatabaseManager
        import sqlite3

        db  = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            # Create user account
            cursor.execute("""
                INSERT INTO users (username, password, role, full_name, email, phone)
                VALUES (?, ?, 'member', ?, ?, ?)
            """, (username, hash_password(password), full_name, email, phone))

            user_id = cursor.lastrowid

            # Create member profile with Basic plan by default
            today = str(date.today())
            cursor.execute("""
                INSERT INTO members
                (user_id, membership_plan, membership_start,
                 membership_end, status)
                VALUES (?, 'Basic', ?, ?, 'Active')
            """, (user_id, today, today))  # Admin upgrades plan later

            conn.commit()
            conn.close()

            # ── Success ───────────────────────────────────────────
            self.reg_msg.config(
                fg="#2ecc71",
                text="✅ Account created! You can now log in."
            )

            # Clear fields and switch to login after 1.5 seconds
            self.root.after(1500, self.show_login_tab)

        except sqlite3.IntegrityError:
            conn.close()
            self.reg_msg.config(
                fg=ACCENT_COLOR,
                text="✗ Username already taken. Please choose another."
            )

    # ── Dashboard Redirect ────────────────────────────────────────

    def open_dashboard(self, user_data):
        """Hides login and opens the correct dashboard."""
        self.root.withdraw()
        dashboard_window = tk.Toplevel(self.root)
        dashboard_window.protocol("WM_DELETE_WINDOW", self.root.destroy)

        if user_data["role"] == "admin":
            from models.admin import Admin
            from gui.admin_dashboard import AdminDashboard
            user = Admin(
                user_data["id"], user_data["username"],
                user_data["full_name"],
                user_data["email"] or "",
                user_data["phone"] or ""
            )
            AdminDashboard(dashboard_window, user)
        else:
            from models.member import Member
            from gui.member_dashboard import MemberDashboard
            user = Member(
                user_data["id"], user_data["username"],
                user_data["full_name"],
                user_data["email"] or "",
                user_data["phone"] or ""
            )
            MemberDashboard(dashboard_window, user)

    # ── Widget Helpers ────────────────────────────────────────────

    def _label(self, text):
        tk.Label(
            self.card, text=text,
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w")

    def _entry(self, parent=None, show=""):
        parent = parent or self.card
        var = tk.StringVar()
        e = tk.Entry(
            parent,
            textvariable=var,
            font=("Arial", 11),
            bg=INPUT_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat", bd=0,
            show=show
        )
        e.pack(fill="x", ipady=7, pady=(1, 0))
        e.get = var.get  # shortcut so we can call entry.get()
        return e

    
