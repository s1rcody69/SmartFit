# Main entrypoint - run this file to start app

import tkinter as tk
from database.db_manager import DatabaseManager
from gui.login_screen import LoginScreen


def main():
    print("Starting SmartFit Gym System...")

    # Step 1: Initialize database and create tables
    db = DatabaseManager()

    # Step 2: Seed default admin and plans (only runs if empty)
    db.seed_default_data()

    # Step 3: Launch the login window
    root = tk.Tk()
    LoginScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()