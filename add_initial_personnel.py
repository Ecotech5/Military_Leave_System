#!/usr/bin/env python3
"""
Add initial personnel to the database (Admin Officer, Commander, RSM)
Run this ONCE after creating the database
"""

import sqlite3
from datetime import datetime

DB_PATH = 'database/military_leave_system.db'


def add_initial_personnel():
    """Add the initial personnel needed to log in"""

    print("=" * 60)
    print("ADDING INITIAL PERSONNEL TO DATABASE")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if personnel already exist
    cursor.execute("SELECT COUNT(*) FROM personnel")
    count = cursor.fetchone()[0]

    if count > 0:
        print(f"\n[INFO] Database already has {count} personnel records.")
        response = input(
            "Do you want to add initial personnel anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            conn.close()
            return

    print("\n[1/4] Adding Admin Officer...")

    # Get rank order for Admin Officer
    cursor.execute(
        "SELECT rank_order FROM ranks WHERE rank_name = 'Admin Officer'")
    result = cursor.fetchone()
    if result:
        ao_rank_order = result[0]
    else:
        ao_rank_order = 11  # Default fallback

    # Insert Admin Officer
    cursor.execute("""
        INSERT OR IGNORE INTO personnel (
            service_number, name, rank, rank_category, rank_order, unit, email, phone, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('NACWC/ADMIN', 'Admin Officer', 'Admin Officer', 'officer', ao_rank_order,
          'NACWC', 'admin@mil.ng', '08012340001', 1))

    ao_id = cursor.lastrowid
    if ao_id:
        print(f"  ✓ Admin Officer added (ID: {ao_id})")
    else:
        print("  ⚠ Admin Officer already exists")
        cursor.execute("SELECT id FROM personnel WHERE rank = 'Admin Officer'")
        ao_id = cursor.fetchone()[0]

    print("\n[2/4] Adding Commander...")

    # Get rank order for Major General
    cursor.execute(
        "SELECT rank_order FROM ranks WHERE rank_name = 'MAJOR GENERAL'")
    result = cursor.fetchone()
    if result:
        cdr_rank_order = result[0]
    else:
        cdr_rank_order = 5  # Default fallback

    # Insert Commander
    cursor.execute("""
        INSERT OR IGNORE INTO personnel (
            service_number, name, rank, rank_category, rank_order, unit, email, phone, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('NACWC/COM', 'Commander', 'Major General', 'officer', cdr_rank_order,
          'NACWC', 'commander@mil.ng', '08012340002', 1))

    cdr_id = cursor.lastrowid
    if cdr_id:
        print(f"   Commander added (ID: {cdr_id})")
    else:
        print("   Commander already exists")
        cursor.execute(
            "SELECT id FROM personnel WHERE rank = 'Major General'")
        cdr_id = cursor.fetchone()[0]

    print("\n[3/4] Adding RSM...")

    # Get rank order for RSM
    cursor.execute("SELECT rank_order FROM ranks WHERE rank_name = 'RSM'")
    result = cursor.fetchone()
    if result:
        rsm_rank_order = result[0]
    else:
        rsm_rank_order = 9  # Default fallback

    # Insert RSM
    cursor.execute("""
        INSERT OR IGNORE INTO personnel (
            service_number, name, rank, rank_category, rank_order, unit, email, phone, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('NACWC/RSM', 'RSM', 'ARMY WARRANT OFFICER', 'soldier', rsm_rank_order,
          'NACWC', 'rsm@mil.ng', '08012340003', 1))

    rsm_id = cursor.lastrowid
    if rsm_id:
        print(f"   RSM added (ID: {rsm_id})")
    else:
        print("   RSM already exists")
        cursor.execute("SELECT id FROM personnel WHERE rank = 'RSM'")
        rsm_id = cursor.fetchone()[0]

    print("\n[4/4] Adding sample soldier for testing...")

    # Get rank order for Private
    cursor.execute("SELECT rank_order FROM ranks WHERE rank_name = 'Private'")
    result = cursor.fetchone()
    if result:
        private_rank_order = result[0]
    else:
        private_rank_order = 1  # Default fallback

    # Create leave entitlements for all personnel
    print("\n[5/5] Creating leave entitlements (14 days each)...")

    cursor.execute("SELECT id FROM personnel WHERE is_active = 1")
    all_personnel = cursor.fetchall()
    current_year = datetime.now().year

    for person in all_personnel:
        cursor.execute("""
            INSERT OR IGNORE INTO leave_entitlement (personnel_id, year, total_days_entitled, days_used, days_remaining)
            VALUES (?, ?, 14, 0, 14)
        """, (person[0], current_year))

    print(f"   Created leave entitlements for {len(all_personnel)} personnel")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("INITIAL PERSONNEL ADDED SUCCESSFULLY!")
    print("=" * 60)

    print("-" * 40)
    print("\nNext step: Run 'python app.py' and log in!")


if __name__ == "__main__":
    add_initial_personnel()
