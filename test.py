# test.py
import sys
print("Python:", sys.version)
print("Current folder:", __import__('os').getcwd())

print("\n--- Testing database ---")
from database.db_manager import DatabaseManager
db = DatabaseManager()
print("✅ Database OK")

print("\n--- Testing auth ---")
from utils.auth import verify_login
result = verify_login("admin", "admin123")
print("Login result:", result)

print("\n--- Testing Admin model ---")
from models.admin import Admin
admin = Admin(result["id"], result["username"], result["full_name"])
print("✅ Admin model OK:", admin)

print("\n--- Testing GUI import ---")
from gui.admin_dashboard import AdminDashboard
print("✅ AdminDashboard import OK")

print("\nAll tests passed!")