#!/usr/bin/env python3
"""
INSERT examples for adding new data
"""

import sqlite3
from datetime import date, timedelta


def add_new_soldier():
    """Example: Add a new soldier to the system"""
    print("=" * 60)
    print("EXAMPLE: ADD NEW SOLDIER")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    new_soldier = {
        'service_number': 'NG/A/008',
        'name': 'David Okafor',
        'rank': 'Private',
        'rank_category': 'soldier',
        'rank_order': 1,
        'unit': '1st Battalion',
        'platoon': '3rd Platoon',
        'company': 'Alpha Company',
        'email': 'david.okafor@test.mil.ng',
        'phone': '+2348012345014',
        'address': 'Test Address 14',
        'date_of_birth': '1995-03-20',
        'date_of_enlistment': '2018-06-15',
        'next_of_kin': 'Mrs. Okafor',
        'next_of_kin_phone': '+2348012345014'
    }

    cursor.execute('''
        INSERT INTO personnel 
        (service_number, name, rank, rank_category, rank_order, unit, platoon, company,
         email, phone, address, date_of_birth, date_of_enlistment, next_of_kin, next_of_kin_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        new_soldier['service_number'], new_soldier['name'], new_soldier['rank'],
        new_soldier['rank_category'], new_soldier['rank_order'], new_soldier['unit'],
        new_soldier['platoon'], new_soldier['company'], new_soldier['email'],
        new_soldier['phone'], new_soldier['address'], new_soldier['date_of_birth'],
        new_soldier['date_of_enlistment'], new_soldier['next_of_kin'],
        new_soldier['next_of_kin_phone']
    ))

    personnel_id = cursor.lastrowid

    # Add leave entitlement for current year
    current_year = date.today().year
    cursor.execute('''
        INSERT INTO leave_entitlement (personnel_id, year, total_days_entitled, days_used, days_remaining)
        VALUES (?, ?, 14, 0, 14)
    ''', (personnel_id, current_year))

    # Add off-duty schedule (weekends off)
    for day in [5, 6]:  # Saturday, Sunday
        cursor.execute('''
            INSERT INTO off_duty_schedule (personnel_id, day_of_week, is_off_duty, notes)
            VALUES (?, ?, 1, 'Weekend off')
        ''', (personnel_id, day))

    conn.commit()
    print(
        f"✓ Added new soldier: {new_soldier['name']} ({new_soldier['service_number']})")
    print(f"✓ Personnel ID: {personnel_id}")

    conn.close()


def add_new_leave_request():
    """Example: Add a new leave request"""
    print("\n" + "=" * 60)
    print("EXAMPLE: ADD NEW LEAVE REQUEST")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Get personnel ID
    cursor.execute(
        "SELECT id FROM personnel WHERE service_number = ?", ("NG/A/008",))
    row = cursor.fetchone()

    if row:
        personnel_id = row[0]
        start_date = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=35)).strftime('%Y-%m-%d')
        total_days = 6

        cursor.execute('''
            INSERT INTO leave_requests 
            (personnel_id, leave_type, start_date, end_date, total_days, reason, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (personnel_id, 'annual', start_date, end_date, total_days,
              'End of year leave', 'pending_rsm'))

        request_id = cursor.lastrowid
        conn.commit()

        print(f"✓ Added leave request ID: {request_id}")
        print(f"  Personnel: NG/A/008")
        print(f"  Dates: {start_date} to {end_date}")
        print(f"  Days: {total_days}")

    conn.close()


def add_off_duty_exception():
    """Example: Request temporary off-duty exception"""
    print("\n" + "=" * 60)
    print("EXAMPLE: ADD OFF-DUTY EXCEPTION REQUEST")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM personnel WHERE service_number = ?", ("NG/A/002",))
    row = cursor.fetchone()

    if row:
        personnel_id = row[0]
        exception_date = (date.today() + timedelta(days=15)
                          ).strftime('%Y-%m-%d')

        cursor.execute('''
            INSERT INTO off_duty_exceptions 
            (personnel_id, exception_date, is_off_duty, reason, status)
            VALUES (?, ?, 1, 'Medical appointment', 'pending')
        ''', (personnel_id, exception_date))

        exception_id = cursor.lastrowid
        conn.commit()

        print(f"✓ Added off-duty exception request ID: {exception_id}")
        print(f"  Personnel: NG/A/002")
        print(f"  Date: {exception_date}")
        print(f"  Status: pending")

    conn.close()


def add_duty_type():
    """Example: Add a new duty type"""
    print("\n" + "=" * 60)
    print("EXAMPLE: ADD NEW DUTY TYPE")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    new_duty = {
        'duty_name': 'Training Duty',
        'category': 'both',
        'default_shift': 'morning',
        'requires_supervisor': 1,
        'description': 'Training and exercise coordination'
    }

    cursor.execute('''
        INSERT INTO duty_types 
        (duty_name, category, default_shift, requires_supervisor, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        new_duty['duty_name'], new_duty['category'], new_duty['default_shift'],
        new_duty['requires_supervisor'], new_duty['description']
    ))

    duty_id = cursor.lastrowid
    conn.commit()

    print(f"✓ Added new duty type: {new_duty['duty_name']}")
    print(f"  Duty ID: {duty_id}")
    print(f"  Category: {new_duty['category']}")

    conn.close()


def add_multiple_leave_requests_batch():
    """Example: Batch insert multiple leave requests"""
    print("\n" + "=" * 60)
    print("EXAMPLE: BATCH INSERT LEAVE REQUESTS")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Get all active personnel
    cursor.execute(
        "SELECT id, service_number FROM personnel WHERE is_active = 1")
    personnel_list = cursor.fetchall()

    leave_requests = []
    # First 5 personnel
    for i, (personnel_id, service_number) in enumerate(personnel_list[:5]):
        start_date = (date.today() + timedelta(days=45 + i)
                      ).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=50 + i)).strftime('%Y-%m-%d')
        total_days = 6

        leave_requests.append((
            personnel_id, 'annual', start_date, end_date, total_days,
            f'Batch submitted leave request', 'pending_rsm' if i < 3 else 'pending_ao'
        ))

    cursor.executemany('''
        INSERT INTO leave_requests 
        (personnel_id, leave_type, start_date, end_date, total_days, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', leave_requests)

    conn.commit()
    print(f"✓ Batch inserted {len(leave_requests)} leave requests")

    conn.close()


if __name__ == "__main__":
    add_new_soldier()
    add_new_leave_request()
    add_off_duty_exception()
    add_duty_type()
    add_multiple_leave_requests_batch()
    print("\n" + "=" * 60)
    print("ALL INSERT EXAMPLES COMPLETED")
    print("=" * 60)
