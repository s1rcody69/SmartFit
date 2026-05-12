

import tkinter as tk
from tkinter import messagebox
from utils.auth import verify_login

# Color Pallete
BG_COLOR      = "#1a1a2e"   # Dark navy background
CARD_COLOR    = "#16213e"   # Slightly lighter card
ACCENT_COLOR  = "#e94560"   # Red accent
TEXT_COLOR    = "#eaeaea"   # Light text
SUBTEXT_COLOR = "#a0a0b0"   # Grey subtext
INPUT_BG      = "#0f3460"   # Input field background
BTN_COLOR     = "#e94560"   # Button color
BTN_HOVER     = "#c73652"   # Button hover


# Smartfit login window
class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartFit Gym System ~ Login")
        self.root.geometry("480x580")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Center window screen
        self.center_window(480,580)
        self.build_ui()

    def center_window(self, width, height):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h- height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")


    # Builds the widgets on the login screen
    def build_ui(self): # FIXED: Indented to be inside the class

        # LOGO/HEADER
        header_frame = tk.Frame(self.root, bg=BG_COLOR)
        header_frame.pack(pady=(50,10))

        tk.Label(
            header_frame,
            text="",
            font=("Arial", 48),
            bg=BG_COLOR,
            fg=ACCENT_COLOR
        ).pack()

        tk.Label(
            header_frame,
            text="Gym Management System",
            font=("Arial", 11),
            bg=BG_COLOR,
            fg=SUBTEXT_COLOR
        ).pack()

        # Login Card
        card = tk.Frame(self.root, bg=CARD_COLOR, padx=40, pady=30)
        card.pack(padx=40, pady=20, fill="x")

        tk.Label(
            card,
            text="Sign In to Your Account",
            font=("Arial", 13),
            bg=CARD_COLOR,
            fg=TEXT_COLOR

        ).pack(anchor="w", pady=(0, 20))

        # Username feild
        tk.Label(
            card,
            text="Username",
            font=("Arial", 10),
            bg=CARD_COLOR,
            fg=SUBTEXT_COLOR
        ).pack(anchor="w")

        self.username_var = tk.StringVar()
        username_entry = tk.Entry(
            card,
            textvariable=self.username_var,
            font=("Arial", 12),
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat",
            bd=0
        )
        username_entry.pack(fill="x", ipady=8, pady=(4, 14))

        # Password Feild
        tk.Label(
            card,
            text="Password",
            font=("Arial", 10),
            bg=CARD_COLOR,
            fg=SUBTEXT_COLOR
        ).pack(anchor="w")

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            card,
            textvariable=self.password_var,
            font=("Arial", 12),
            bg=INPUT_BG,
            fg= TEXT_COLOR,
            show="●",
            relief="flat",
            bd=0
        )
        self.password_entry.pack(fill="x", ipady=8, pady=(4, 6)) # FIXED: Added .pack()

        #Hide/Show password toggle
        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(
            card,
            text="Show password",
            variable=self.show_pw, # FIXED: Added variable so toggle works
            command=self.toggle_password,
            bg=CARD_COLOR,
            fg=SUBTEXT_COLOR,
            activebackground=CARD_COLOR,
            font=("Arial", 9)
        ).pack(anchor="w", pady=(0, 16)) # FIXED: paddy to pady

        # Login button
        self.login_btn = tk.Button(
            card,
            text="LOGIN",
            font=("Arial", 12, "bold"),
            bg=BTN_COLOR,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.attempt_login
        )
        self.login_btn.pack(fill="x", ipady=10)
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=BTN_HOVER))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=BTN_COLOR))

        # Error label(hidden by default)
        self.error_label = tk.Label(
            card,
            text="",
            font=("Arial", 10),
            bg=CARD_COLOR,
            fg=ACCENT_COLOR
        )
        self.error_label.pack(pady=(10,0))

        # Footer
        tk.Label(
            self.root,
            text="Default Admin → username: admin | password: admin123",
            font=("Arial", 8),
            bg=BG_COLOR,
            fg=SUBTEXT_COLOR
        ).pack(pady=(0, 10))

        # Allow pressing Enter to login
        self.root.bind("<Return>", lambda e: self.attempt_login())

    
    # Shows or hide password characters
    def toggle_password(self):
        if self.show_pw.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="●")

    # Validates credentials and opens the correct dashboard
    def attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.error_label.config(text="⚠ Please enter username and password.")
            return
        
        user_data = verify_login(username, password)

        if user_data is None:
            self.error_label.config(text="✗ Invalid username or password.")
            return
        
        # Login successful - oppen corect dashboard
        self.open_dashboard(user_data)

    # Closes open window and opens the right dashboard
    def open_dashboard(self, user_data):
       
        self.root.destroy()

        new_root = tk.Tk()

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
            AdminDashboard(new_root, user)

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
            MemberDashboard(new_root, user)

        new_root.mainloop()

    
