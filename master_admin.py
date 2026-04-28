# create_master_admin.py
import sqlite3
import hashlib

DB_PATH = 'database/military_leave_system.db'


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# First, clear all existing personnel (fresh start)
cursor.execute("DELETE FROM personnel")
cursor.execute("DELETE FROM leave_entitlement")
print("✓ Cleared existing personnel")

# Create master admin (YOU)
master_password_hash = hash_password("NACWCCORPERS/123456")

cursor.execute("""
    INSERT INTO personnel (
        service_number, name, rank, rank_category, rank_order, 
        unit, email, phone, password, force_password_change, is_active
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    'NACWCCORPERS',           # service_number
    'System Administrator',    # name
    'Admin',                   # rank
    'officer',                 # rank_category
    100,                       # rank_order (highest)
    'HQ',                      # unit
    'admin@system.mil.ng',     # email
    '08000000000',             # phone
    master_password_hash,      # password
    # force_password_change (0 = no, master admin doesn't need to change)
    0,
    1                          # is_active
))

conn.commit()
print("✓ Master admin account created:")
print("  Service Number: NACWCCORPERS")
print("  Password: NACWCCORPERS/123456")
print("  Role: Can add/remove personnel (backdoor access)")

conn.close()

print("\n" + "=" * 50)
print("SETUP COMPLETE!")
print("=" * 50)
print("\nNo other users exist. You must add them through the web interface.")
print("Login with: NACWCCORPERS / NACWCCORPERS/123456")
