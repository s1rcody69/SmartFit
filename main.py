import tkinter as tk
from database.db_manager import DatabaseManager
from gui.login_screen import LoginScreen


def main():
    print("Starting SmartFit Gym System...")

    # Initialize database
    db = DatabaseManager()
    db.seed_default_data()

    # Launch login window
    root = tk.Tk()
    LoginScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()