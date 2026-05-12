# gui/admin_dashboard.py
import tkinter as tk

class AdminDashboard:
    def __init__(self, root, user):
        self.root = root
        self.root.title(user.get_dashboard_title())
        self.root.geometry("1100x680")
        self.root.configure(bg="#1a1a2e")
        tk.Label(
            self.root,
            text=f"✅ Admin Dashboard — Welcome {user.full_name}\n(Full UI coming Day 2)",
            font=("Arial", 18),
            bg="#1a1a2e",
            fg="white"
        ).pack(expand=True)