import tkinter as tk
from database.db_manager import DatabaseManager
from gui.login_screen import LoginScreen


def main():
    print("Starting SmartFit Gym System...")

    # Initialise database and seed default data
    db = DatabaseManager()
    db.seed_default_data()

    # Create ONE root window that lives forever
    root = tk.Tk()

    # Start the login screen
    LoginScreen(root)

    # Hand control to Tkinter — this never returns until
    # the user closes the last window
    root.mainloop()


if __name__ == "__main__":
    main()