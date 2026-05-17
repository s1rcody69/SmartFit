# =============================================================
# The first screen users see when the app starts.
# Contains two tabs:
#   Login    — existing users sign in
#   Register — new members create an account
#
# OOP Concept - ENCAPSULATION:
# All login and registration logic is contained in this one
# class. The outside world just calls LoginScreen(root) and
# this class manages everything internally.
# =============================================================

import tkinter as tk
from tkinter import messagebox
from utils.auth import verify_login
from datetime import date

# Colours used on this screen
BG_COLOR      = "#1a1a2e"
CARD_COLOR    = "#16213e"
ACCENT_COLOR  = "#e94560"
TEXT_COLOR    = "#eaeaea"
SUBTEXT_COLOR = "#a0a0b0"
INPUT_BG      = "#0f3460"
BTN_COLOR     = "#e94560"
BTN_HOVER     = "#c73652"
TAB_INACTIVE  = "#0f3460"


class LoginScreen:
    """
    Manages the login and registration window.

    Responsibilities:
      - Display the Login tab (username + password form)
      - Display the Register tab (new member sign-up form)
      - Validate all form inputs before submitting
      - Hash passwords before saving to the database
      - Redirect users to the correct dashboard after login
    """

    def __init__(self, root):
        """
        Sets up the main window and builds the UI.

        Parameters:
            root — the root tk.Tk() window passed from main.py
        """
        self.root = root
        self.root.title("SmartFit Gym System")
        # FIX: increased height from 620 to 720 so the register form
        # and its CREATE ACCOUNT button are fully visible
        self.root.geometry("500x720")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Centre the window on the screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"500x720+{(sw - 500) // 2}+{(sh - 720) // 2}")

        self._build()

    def _build(self):
        """
        Builds the full login screen layout:
        header -> tab bar -> card area -> footer hint.
        The card area is swapped out when switching tabs.
        """

        # ── App header ────────────────────────────────────────
        h = tk.Frame(self.root, bg=BG_COLOR)
        h.pack(pady=(40, 0))

        tk.Label(
            h, text="SMARTFIT",
            font=("Arial", 30, "bold"),
            bg=BG_COLOR, fg=ACCENT_COLOR
        ).pack()

        tk.Label(
            h, text="GYM MANAGEMENT SYSTEM",
            font=("Arial", 10, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR
        ).pack()

        # Decorative underline
        tk.Label(
            h, text="___________________________",
            font=("Arial", 10),
            bg=BG_COLOR, fg=ACCENT_COLOR
        ).pack(pady=(4, 0))

        # ── Tab switcher bar ──────────────────────────────────
        # Two buttons side by side — clicking swaps the card content
        tab_bar = tk.Frame(self.root, bg=BG_COLOR)
        tab_bar.pack(fill="x", padx=40, pady=(20, 0))

        self._login_tab = tk.Button(
            tab_bar, text="LOGIN",
            font=("Arial", 11, "bold"),
            bg=ACCENT_COLOR, fg="white",
            relief="flat", cursor="hand2",
            command=self._show_login
        )
        self._login_tab.pack(side="left", expand=True, fill="x", ipady=8)

        self._reg_tab = tk.Button(
            tab_bar, text="REGISTER",
            font=("Arial", 11, "bold"),
            bg=TAB_INACTIVE, fg=SUBTEXT_COLOR,
            relief="flat", cursor="hand2",
            command=self._show_register
        )
        self._reg_tab.pack(side="left", expand=True, fill="x", ipady=8)

        # ── Card area ─────────────────────────────────────────
        # This frame is cleared and rebuilt each time a tab is clicked
        self.card = tk.Frame(
            self.root, bg=CARD_COLOR, padx=36, pady=24
        )
        self.card.pack(padx=40, pady=10, fill="both", expand=True)

        # ── Admin hint at the bottom ──────────────────────────
        tk.Label(
            self.root,
            text="Admin login  ->  username: admin   password: admin123",
            font=("Arial", 8),
            bg=BG_COLOR, fg=SUBTEXT_COLOR
        ).pack(pady=(0, 10))

        # Show the login form by default when the window opens
        self._show_login()

    # ── Tab switching ─────────────────────────────────────────

    def _show_login(self):
        """Activates the Login tab and renders the login form."""
        self._login_tab.config(bg=ACCENT_COLOR,  fg="white")
        self._reg_tab.config(bg=TAB_INACTIVE,    fg=SUBTEXT_COLOR)
        self._clear_card()
        self._build_login()

    def _show_register(self):
        """Activates the Register tab and renders the sign-up form."""
        self._reg_tab.config(bg=ACCENT_COLOR,    fg="white")
        self._login_tab.config(bg=TAB_INACTIVE,  fg=SUBTEXT_COLOR)
        self._clear_card()
        self._build_register()

    def _clear_card(self):
        """Removes all widgets from the card area before rebuilding."""
        for widget in self.card.winfo_children():
            widget.destroy()

    # ── Login form ────────────────────────────────────────────

    def _build_login(self):
        """
        Builds the login form inside the card area.
        Fields: username, password, show-password checkbox.
        On submit: validates input, verifies against the database,
        then opens the correct dashboard.
        """
        tk.Label(
            self.card, text="Welcome Back",
            font=("Arial", 14, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            self.card, text="Sign in to your account",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w", pady=(0, 16))

        # Input fields
        self._lu = self._field("Username")
        self._lp = self._field("Password", show="*")

        # Toggle to reveal/hide the password characters
        self._show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.card, text="Show password",
            variable=self._show_var,
            command=lambda: self._lp.config(
                show="" if self._show_var.get() else "*"),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR,
            selectcolor=CARD_COLOR,
            activebackground=CARD_COLOR,
            font=("Arial", 9)
        ).pack(anchor="w", pady=(0, 16))

        # Error message label — hidden until a login fails
        self._login_err = tk.Label(
            self.card, text="",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=ACCENT_COLOR
        )

        # Login button with hover colour change
        b = tk.Button(
            self.card, text="LOGIN",
            font=("Arial", 12, "bold"),
            bg=BTN_COLOR, fg="white",
            relief="flat", cursor="hand2",
            command=self._attempt_login
        )
        b.pack(fill="x", ipady=10)
        b.bind("<Enter>", lambda e: b.config(bg=BTN_HOVER))
        b.bind("<Leave>", lambda e: b.config(bg=BTN_COLOR))

        self._login_err.pack(pady=(10, 0))

        # Link to the register tab
        tk.Label(
            self.card, text="Don't have an account?",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(pady=(14, 0))

        tk.Button(
            self.card, text="Create one here",
            font=("Arial", 9, "underline"),
            bg=CARD_COLOR, fg=ACCENT_COLOR,
            relief="flat", cursor="hand2",
            activebackground=CARD_COLOR,
            command=self._show_register
        ).pack()

        # Allow pressing Enter to submit the login form
        self.root.bind("<Return>", lambda e: self._attempt_login())

    # ── Register form ─────────────────────────────────────────

    def _build_register(self):
        """
        Builds the new member registration form.
        Fields: full name, phone, email, username, password x2.
        On submit: validates, hashes password, saves to database,
        then auto-switches to the login tab on success.
        """
        tk.Label(
            self.card, text="Create Account",
            font=("Arial", 14, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            self.card, text="Register as a new gym member",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w", pady=(0, 14))

        # Row 1 — two columns: Full Name | Phone
        r1 = tk.Frame(self.card, bg=CARD_COLOR); r1.pack(fill="x")
        lc = tk.Frame(r1, bg=CARD_COLOR)
        lc.pack(side="left", expand=True, fill="x", padx=(0, 6))
        rc = tk.Frame(r1, bg=CARD_COLOR)
        rc.pack(side="left", expand=True, fill="x")

        self._rn  = self._field("Full Name", parent=lc)
        self._rph = self._field("Phone",     parent=rc)

        # Single-column fields
        self._re = self._field("Email")
        self._ru = self._field("Username")

        # Row 2 — two columns: Password | Confirm Password
        r2 = tk.Frame(self.card, bg=CARD_COLOR); r2.pack(fill="x")
        lc2 = tk.Frame(r2, bg=CARD_COLOR)
        lc2.pack(side="left", expand=True, fill="x", padx=(0, 6))
        rc2 = tk.Frame(r2, bg=CARD_COLOR)
        rc2.pack(side="left", expand=True, fill="x")

        self._rpw  = self._field("Password",         parent=lc2, show="*")
        self._rpw2 = self._field("Confirm Password", parent=rc2, show="*")

        # Register submit button
        b = tk.Button(
            self.card, text="CREATE ACCOUNT",
            font=("Arial", 12, "bold"),
            bg=BTN_COLOR, fg="white",
            relief="flat", cursor="hand2",
            command=self._attempt_register
        )
        b.pack(fill="x", ipady=10, pady=(12, 0))
        b.bind("<Enter>", lambda e: b.config(bg=BTN_HOVER))
        b.bind("<Leave>", lambda e: b.config(bg=BTN_COLOR))

        # Feedback label for success/error messages
        self._reg_msg = tk.Label(
            self.card, text="",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=ACCENT_COLOR,
            wraplength=380
        )
        self._reg_msg.pack(pady=(8, 0))

        # Link back to login tab
        tk.Label(
            self.card, text="Already have an account?",
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(pady=(10, 0))

        tk.Button(
            self.card, text="Sign in here",
            font=("Arial", 9, "underline"),
            bg=CARD_COLOR, fg=ACCENT_COLOR,
            relief="flat", cursor="hand2",
            activebackground=CARD_COLOR,
            command=self._show_login
        ).pack()

    # ── Authentication logic ──────────────────────────────────

    def _attempt_login(self):
        """
        Reads the login form, validates input, then calls
        verify_login() from utils/auth.py to check credentials.
        On success redirects to the correct dashboard.
        On failure shows an inline error message.
        """
        username = self._lu.var.get().strip()
        password = self._lp.var.get().strip()

        # Basic empty field check
        if not username or not password:
            self._login_err.config(
                text="Please enter username and password.")
            return

        # Check credentials against the database
        user_data = verify_login(username, password)

        if not user_data:
            self._login_err.config(
                text="Invalid username or password.")
            return

        # Credentials valid — open the appropriate dashboard
        self._open_dashboard(user_data)

    def _attempt_register(self):
        """
        Reads the register form, runs validation checks,
        hashes the password, saves the new user + member record
        to the database, then switches to the login tab.

        New members are automatically assigned the Basic plan.
        The admin can upgrade their plan later.
        """
        name  = self._rn.var.get().strip()
        phone = self._rph.var.get().strip()
        email = self._re.var.get().strip()
        uname = self._ru.var.get().strip()
        pw    = self._rpw.var.get().strip()
        pw2   = self._rpw2.var.get().strip()

        # ── Input validation ──────────────────────────────────
        if not name or not uname or not pw:
            self._reg_msg.config(
                fg=ACCENT_COLOR,
                text="Full name, username and password are required.")
            return

        if len(uname) < 3:
            self._reg_msg.config(
                fg=ACCENT_COLOR,
                text="Username must be at least 3 characters.")
            return

        if len(pw) < 6:
            self._reg_msg.config(
                fg=ACCENT_COLOR,
                text="Password must be at least 6 characters.")
            return

        if pw != pw2:
            self._reg_msg.config(
                fg=ACCENT_COLOR, text="Passwords do not match.")
            return

        # ── Save to database ──────────────────────────────────
        from utils.auth import hash_password
        from database.db_manager import DatabaseManager
        import sqlite3

        conn   = DatabaseManager().get_connection()
        cursor = conn.cursor()

        try:
            # Step 1: Create the user account row
            cursor.execute(
                "INSERT INTO users "
                "(username, password, role, full_name, email, phone)"
                " VALUES (?, ?, 'member', ?, ?, ?)",
                (uname, hash_password(pw), name, email, phone)
            )
            user_id = cursor.lastrowid   # get the auto-generated ID

            # Step 2: Create the linked member profile row
            today = str(date.today())
            cursor.execute(
                "INSERT INTO members "
                "(user_id, membership_plan, membership_start,"
                " membership_end, status)"
                " VALUES (?, 'Basic', ?, ?, 'Active')",
                (user_id, today, today)
            )
            conn.commit()

            # Show success and auto-switch to login after 1.5 seconds
            self._reg_msg.config(
                fg="#2ecc71",
                text="Account created! You can now log in.")
            self.root.after(1500, self._show_login)

        except sqlite3.IntegrityError:
            # Username already exists in the database
            self._reg_msg.config(
                fg=ACCENT_COLOR,
                text="Username already taken. Please choose another.")
        finally:
            conn.close()

    # ── Dashboard routing ─────────────────────────────────────

    def _open_dashboard(self, user_data):
        """
        Hides the login window and opens the correct dashboard
        in a new Toplevel window based on the user's role.

        OOP Concept - POLYMORPHISM:
        Both Admin and Member have get_dashboard_title() but
        return different strings. The routing here checks the
        role field to decide which dashboard class to instantiate.

        We hide (withdraw) instead of destroying the root window
        because destroying it would kill the entire Tkinter engine.
        The root is destroyed when the dashboard window is closed.
        """
        self.root.withdraw()   # hide login window

        dashboard_window = tk.Toplevel(self.root)
        # When the dashboard is closed, exit the whole application
        dashboard_window.protocol(
            "WM_DELETE_WINDOW", self.root.destroy)

        if user_data["role"] == "admin":
            from models.admin import Admin
            from gui.admin_dashboard import AdminDashboard

            user = Admin(
                user_data["id"],
                user_data["username"],
                user_data["full_name"],
                user_data["email"] or "",
                user_data["phone"] or ""
            )
            AdminDashboard(dashboard_window, user)

        else:
            from models.member import Member
            from gui.member_dashboard import MemberDashboard

            user = Member(
                user_data["id"],
                user_data["username"],
                user_data["full_name"],
                user_data["email"] or "",
                user_data["phone"] or ""
            )
            MemberDashboard(dashboard_window, user)

    # ── Widget helper ─────────────────────────────────────────

    def _field(self, label_text, show="", parent=None):
        """
        Creates a label + entry pair for the login/register forms.
        Attaches the StringVar as field.var so the caller can
        read the value with field.var.get().

        Parameters:
            label_text — text shown above the field
            show       — mask character for passwords (e.g. "*")
            parent     — parent widget (defaults to self.card)

        Returns the Entry widget with .var attached.
        """
        p = parent or self.card

        tk.Label(
            p, text=label_text,
            font=("Arial", 9),
            bg=CARD_COLOR, fg=SUBTEXT_COLOR
        ).pack(anchor="w")

        var = tk.StringVar()
        e = tk.Entry(
            p,
            textvariable=var,
            font=("Arial", 11),
            bg=INPUT_BG, fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat", bd=0,
            show=show
        )
        e.pack(fill="x", ipady=7, pady=(2, 10))
        e.var = var   # attach so caller can do: field.var.get()
        return e
# # =============================================================
# # The first screen users see when the app starts.
# # Contains two tabs:
# #   Login    — existing users sign in
# #   Register — new members create an account
# #
# # OOP Concept - ENCAPSULATION:
# # All login and registration logic is contained in this one
# # class. The outside world just calls LoginScreen(root) and
# # this class manages everything internally.
# # =============================================================

# import tkinter as tk
# from tkinter import messagebox
# from utils.auth import verify_login
# from datetime import date

# # Colours used on this screen
# BG_COLOR      = "#1a1a2e"
# CARD_COLOR    = "#16213e"
# ACCENT_COLOR  = "#e94560"
# TEXT_COLOR    = "#eaeaea"
# SUBTEXT_COLOR = "#a0a0b0"
# INPUT_BG      = "#0f3460"
# BTN_COLOR     = "#e94560"
# BTN_HOVER     = "#c73652"
# TAB_INACTIVE  = "#0f3460"


# class LoginScreen:
#     """
#     Manages the login and registration window.

#     Responsibilities:
#       - Display the Login tab (username + password form)
#       - Display the Register tab (new member sign-up form)
#       - Validate all form inputs before submitting
#       - Hash passwords before saving to the database
#       - Redirect users to the correct dashboard after login
#     """

#     def __init__(self, root):
#         """
#         Sets up the main window and builds the UI.

#         Parameters:
#             root — the root tk.Tk() window passed from main.py
#         """
#         self.root = root
#         self.root.title("SmartFit Gym System")
#         self.root.geometry("500x620")
#         self.root.configure(bg=BG_COLOR)
#         self.root.resizable(False, False)

#         # Centre the window on the screen
#         sw = self.root.winfo_screenwidth()
#         sh = self.root.winfo_screenheight()
#         self.root.geometry(f"500x620+{(sw - 500) // 2}+{(sh - 620) // 2}")

#         self._build()

#     def _build(self):
#         """
#         Builds the full login screen layout:
#         header -> tab bar -> card area -> footer hint.
#         The card area is swapped out when switching tabs.
#         """

#         # ── App header ────────────────────────────────────────
#         h = tk.Frame(self.root, bg=BG_COLOR)
#         h.pack(pady=(40, 0))

#         tk.Label(
#             h, text="SMARTFIT",
#             font=("Arial", 30, "bold"),
#             bg=BG_COLOR, fg=ACCENT_COLOR
#         ).pack()

#         tk.Label(
#             h, text="GYM MANAGEMENT SYSTEM",
#             font=("Arial", 10, "bold"),
#             bg=BG_COLOR, fg=TEXT_COLOR
#         ).pack()

#         # Decorative underline
#         tk.Label(
#             h, text="___________________________",
#             font=("Arial", 10),
#             bg=BG_COLOR, fg=ACCENT_COLOR
#         ).pack(pady=(4, 0))

#         # ── Tab switcher bar ──────────────────────────────────
#         # Two buttons side by side — clicking swaps the card content
#         tab_bar = tk.Frame(self.root, bg=BG_COLOR)
#         tab_bar.pack(fill="x", padx=40, pady=(20, 0))

#         self._login_tab = tk.Button(
#             tab_bar, text="LOGIN",
#             font=("Arial", 11, "bold"),
#             bg=ACCENT_COLOR, fg="white",
#             relief="flat", cursor="hand2",
#             command=self._show_login
#         )
#         self._login_tab.pack(side="left", expand=True, fill="x", ipady=8)

#         self._reg_tab = tk.Button(
#             tab_bar, text="REGISTER",
#             font=("Arial", 11, "bold"),
#             bg=TAB_INACTIVE, fg=SUBTEXT_COLOR,
#             relief="flat", cursor="hand2",
#             command=self._show_register
#         )
#         self._reg_tab.pack(side="left", expand=True, fill="x", ipady=8)

#         # ── Card area ─────────────────────────────────────────
#         # This frame is cleared and rebuilt each time a tab is clicked
#         self.card = tk.Frame(
#             self.root, bg=CARD_COLOR, padx=36, pady=24
#         )
#         self.card.pack(padx=40, pady=10, fill="both", expand=True)

#         # ── Admin hint at the bottom ──────────────────────────
#         tk.Label(
#             self.root,
#             text="Admin login  ->  username: admin   password: admin123",
#             font=("Arial", 8),
#             bg=BG_COLOR, fg=SUBTEXT_COLOR
#         ).pack(pady=(0, 10))

#         # Show the login form by default when the window opens
#         self._show_login()

#     # ── Tab switching ─────────────────────────────────────────

#     def _show_login(self):
#         """Activates the Login tab and renders the login form."""
#         self._login_tab.config(bg=ACCENT_COLOR,  fg="white")
#         self._reg_tab.config(bg=TAB_INACTIVE,    fg=SUBTEXT_COLOR)
#         self._clear_card()
#         self._build_login()

#     def _show_register(self):
#         """Activates the Register tab and renders the sign-up form."""
#         self._reg_tab.config(bg=ACCENT_COLOR,    fg="white")
#         self._login_tab.config(bg=TAB_INACTIVE,  fg=SUBTEXT_COLOR)
#         self._clear_card()
#         self._build_register()

#     def _clear_card(self):
#         """Removes all widgets from the card area before rebuilding."""
#         for widget in self.card.winfo_children():
#             widget.destroy()

#     # ── Login form ────────────────────────────────────────────

#     def _build_login(self):
#         """
#         Builds the login form inside the card area.
#         Fields: username, password, show-password checkbox.
#         On submit: validates input, verifies against the database,
#         then opens the correct dashboard.
#         """
#         tk.Label(
#             self.card, text="Welcome Back",
#             font=("Arial", 14, "bold"),
#             bg=CARD_COLOR, fg=TEXT_COLOR
#         ).pack(anchor="w", pady=(0, 2))

#         tk.Label(
#             self.card, text="Sign in to your account",
#             font=("Arial", 9),
#             bg=CARD_COLOR, fg=SUBTEXT_COLOR
#         ).pack(anchor="w", pady=(0, 16))

#         # Input fields
#         self._lu = self._field("Username")
#         self._lp = self._field("Password", show="*")

#         # Toggle to reveal/hide the password characters
#         self._show_var = tk.BooleanVar(value=False)
#         tk.Checkbutton(
#             self.card, text="Show password",
#             variable=self._show_var,
#             command=lambda: self._lp.config(
#                 show="" if self._show_var.get() else "*"),
#             bg=CARD_COLOR, fg=SUBTEXT_COLOR,
#             selectcolor=CARD_COLOR,
#             activebackground=CARD_COLOR,
#             font=("Arial", 9)
#         ).pack(anchor="w", pady=(0, 16))

#         # Error message label — hidden until a login fails
#         self._login_err = tk.Label(
#             self.card, text="",
#             font=("Arial", 9),
#             bg=CARD_COLOR, fg=ACCENT_COLOR
#         )

#         # Login button with hover colour change
#         b = tk.Button(
#             self.card, text="LOGIN",
#             font=("Arial", 12, "bold"),
#             bg=BTN_COLOR, fg="white",
#             relief="flat", cursor="hand2",
#             command=self._attempt_login
#         )
#         b.pack(fill="x", ipady=10)
#         b.bind("<Enter>", lambda e: b.config(bg=BTN_HOVER))
#         b.bind("<Leave>", lambda e: b.config(bg=BTN_COLOR))

#         self._login_err.pack(pady=(10, 0))

#         # Link to the register tab
#         tk.Label(
#             self.card, text="Don't have an account?",
#             font=("Arial", 9),
#             bg=CARD_COLOR, fg=SUBTEXT_COLOR
#         ).pack(pady=(14, 0))

#         tk.Button(
#             self.card, text="Create one here",
#             font=("Arial", 9, "underline"),
#             bg=CARD_COLOR, fg=ACCENT_COLOR,
#             relief="flat", cursor="hand2",
#             activebackground=CARD_COLOR,
#             command=self._show_register
#         ).pack()

#         # Allow pressing Enter to submit the login form
#         self.root.bind("<Return>", lambda e: self._attempt_login())

#     # ── Register form ─────────────────────────────────────────

#     def _build_register(self):
#         """
#         Builds the new member registration form.
#         Fields: full name, phone, email, username, password x2.
#         On submit: validates, hashes password, saves to database,
#         then auto-switches to the login tab on success.
#         """
#         tk.Label(
#             self.card, text="Create Account",
#             font=("Arial", 14, "bold"),
#             bg=CARD_COLOR, fg=TEXT_COLOR
#         ).pack(anchor="w", pady=(0, 2))

#         tk.Label(
#             self.card, text="Register as a new gym member",
#             font=("Arial", 9),
#             bg=CARD_COLOR, fg=SUBTEXT_COLOR
#         ).pack(anchor="w", pady=(0, 14))

#         # Row 1 — two columns: Full Name | Phone
#         r1 = tk.Frame(self.card, bg=CARD_COLOR); r1.pack(fill="x")
#         lc = tk.Frame(r1, bg=CARD_COLOR)
#         lc.pack(side="left", expand=True, fill="x", padx=(0, 6))
#         rc = tk.Frame(r1, bg=CARD_COLOR)
#         rc.pack(side="left", expand=True, fill="x")

#         self._rn  = self._field("Full Name", parent=lc)
#         self._rph = self._field("Phone",     parent=rc)

#         # Single-column fields
#         self._re = self._field("Email")
#         self._ru = self._field("Username")

#         # Row 2 — two columns: Password | Confirm Password
#         r2 = tk.Frame(self.card, bg=CARD_COLOR); r2.pack(fill="x")
#         lc2 = tk.Frame(r2, bg=CARD_COLOR)
#         lc2.pack(side="left", expand=True, fill="x", padx=(0, 6))
#         rc2 = tk.Frame(r2, bg=CARD_COLOR)
#         rc2.pack(side="left", expand=True, fill="x")

#         self._rpw  = self._field("Password",         parent=lc2, show="*")
#         self._rpw2 = self._field("Confirm Password", parent=rc2, show="*")

#         # Register submit button
#         b = tk.Button(
#             self.card, text="CREATE ACCOUNT",
#             font=("Arial", 12, "bold"),
#             bg=BTN_COLOR, fg="white",
#             relief="flat", cursor="hand2",
#             command=self._attempt_register
#         )
#         b.pack(fill="x", ipady=10, pady=(12, 0))
#         b.bind("<Enter>", lambda e: b.config(bg=BTN_HOVER))
#         b.bind("<Leave>", lambda e: b.config(bg=BTN_COLOR))

#         # Feedback label for success/error messages
#         self._reg_msg = tk.Label(
#             self.card, text="",
#             font=("Arial", 9),
#             bg=CARD_COLOR, fg=ACCENT_COLOR,
#             wraplength=380
#         )
#         self._reg_msg.pack(pady=(8, 0))

#         # Link back to login tab
#         tk.Label(
#             self.card, text="Already have an account?",
#             font=("Arial", 9),
#             bg=CARD_COLOR, fg=SUBTEXT_COLOR
#         ).pack(pady=(10, 0))

#         tk.Button(
#             self.card, text="Sign in here",
#             font=("Arial", 9, "underline"),
#             bg=CARD_COLOR, fg=ACCENT_COLOR,
#             relief="flat", cursor="hand2",
#             activebackground=CARD_COLOR,
#             command=self._show_login
#         ).pack()

#     # ── Authentication logic ──────────────────────────────────

#     def _attempt_login(self):
#         """
#         Reads the login form, validates input, then calls
#         verify_login() from utils/auth.py to check credentials.
#         On success redirects to the correct dashboard.
#         On failure shows an inline error message.
#         """
#         username = self._lu.var.get().strip()
#         password = self._lp.var.get().strip()

#         # Basic empty field check
#         if not username or not password:
#             self._login_err.config(
#                 text="Please enter username and password.")
#             return

#         # Check credentials against the database
#         user_data = verify_login(username, password)

#         if not user_data:
#             self._login_err.config(
#                 text="Invalid username or password.")
#             return

#         # Credentials valid — open the appropriate dashboard
#         self._open_dashboard(user_data)

#     def _attempt_register(self):
#         """
#         Reads the register form, runs validation checks,
#         hashes the password, saves the new user + member record
#         to the database, then switches to the login tab.

#         New members are automatically assigned the Basic plan.
#         The admin can upgrade their plan later.
#         """
#         name  = self._rn.var.get().strip()
#         phone = self._rph.var.get().strip()
#         email = self._re.var.get().strip()
#         uname = self._ru.var.get().strip()
#         pw    = self._rpw.var.get().strip()
#         pw2   = self._rpw2.var.get().strip()

#         # ── Input validation ──────────────────────────────────
#         if not name or not uname or not pw:
#             self._reg_msg.config(
#                 fg=ACCENT_COLOR,
#                 text="Full name, username and password are required.")
#             return

#         if len(uname) < 3:
#             self._reg_msg.config(
#                 fg=ACCENT_COLOR,
#                 text="Username must be at least 3 characters.")
#             return

#         if len(pw) < 6:
#             self._reg_msg.config(
#                 fg=ACCENT_COLOR,
#                 text="Password must be at least 6 characters.")
#             return

#         if pw != pw2:
#             self._reg_msg.config(
#                 fg=ACCENT_COLOR, text="Passwords do not match.")
#             return

#         # ── Save to database ──────────────────────────────────
#         from utils.auth import hash_password
#         from database.db_manager import DatabaseManager
#         import sqlite3

#         conn   = DatabaseManager().get_connection()
#         cursor = conn.cursor()

#         try:
#             # Step 1: Create the user account row
#             cursor.execute(
#                 "INSERT INTO users "
#                 "(username, password, role, full_name, email, phone)"
#                 " VALUES (?, ?, 'member', ?, ?, ?)",
#                 (uname, hash_password(pw), name, email, phone)
#             )
#             user_id = cursor.lastrowid   # get the auto-generated ID

#             # Step 2: Create the linked member profile row
#             today = str(date.today())
#             cursor.execute(
#                 "INSERT INTO members "
#                 "(user_id, membership_plan, membership_start,"
#                 " membership_end, status)"
#                 " VALUES (?, 'Basic', ?, ?, 'Active')",
#                 (user_id, today, today)
#             )
#             conn.commit()

#             # Show success and auto-switch to login after 1.5 seconds
#             self._reg_msg.config(
#                 fg="#2ecc71",
#                 text="Account created! You can now log in.")
#             self.root.after(1500, self._show_login)

#         except sqlite3.IntegrityError:
#             # Username already exists in the database
#             self._reg_msg.config(
#                 fg=ACCENT_COLOR,
#                 text="Username already taken. Please choose another.")
#         finally:
#             conn.close()

#     # ── Dashboard routing ─────────────────────────────────────

#     def _open_dashboard(self, user_data):
#         """
#         Hides the login window and opens the correct dashboard
#         in a new Toplevel window based on the user's role.

#         OOP Concept - POLYMORPHISM:
#         Both Admin and Member have get_dashboard_title() but
#         return different strings. The routing here checks the
#         role field to decide which dashboard class to instantiate.

#         We hide (withdraw) instead of destroying the root window
#         because destroying it would kill the entire Tkinter engine.
#         The root is destroyed when the dashboard window is closed.
#         """
#         self.root.withdraw()   # hide login window

#         dashboard_window = tk.Toplevel(self.root)
#         # When the dashboard is closed, exit the whole application
#         dashboard_window.protocol(
#             "WM_DELETE_WINDOW", self.root.destroy)

#         if user_data["role"] == "admin":
#             from models.admin import Admin
#             from gui.admin_dashboard import AdminDashboard

#             user = Admin(
#                 user_data["id"],
#                 user_data["username"],
#                 user_data["full_name"],
#                 user_data["email"] or "",
#                 user_data["phone"] or ""
#             )
#             AdminDashboard(dashboard_window, user)

#         else:
#             from models.member import Member
#             from gui.member_dashboard import MemberDashboard

#             user = Member(
#                 user_data["id"],
#                 user_data["username"],
#                 user_data["full_name"],
#                 user_data["email"] or "",
#                 user_data["phone"] or ""
#             )
#             MemberDashboard(dashboard_window, user)

#     # ── Widget helper ─────────────────────────────────────────

#     def _field(self, label_text, show="", parent=None):
#         """
#         Creates a label + entry pair for the login/register forms.
#         Attaches the StringVar as field.var so the caller can
#         read the value with field.var.get().

#         Parameters:
#             label_text — text shown above the field
#             show       — mask character for passwords (e.g. "*")
#             parent     — parent widget (defaults to self.card)

#         Returns the Entry widget with .var attached.
#         """
#         p = parent or self.card

#         tk.Label(
#             p, text=label_text,
#             font=("Arial", 9),
#             bg=CARD_COLOR, fg=SUBTEXT_COLOR
#         ).pack(anchor="w")

#         var = tk.StringVar()
#         e = tk.Entry(
#             p,
#             textvariable=var,
#             font=("Arial", 11),
#             bg=INPUT_BG, fg=TEXT_COLOR,
#             insertbackground=TEXT_COLOR,
#             relief="flat", bd=0,
#             show=show
#         )
#         e.pack(fill="x", ipady=7, pady=(2, 10))
#         e.var = var   # attach so caller can do: field.var.get()
#         return e