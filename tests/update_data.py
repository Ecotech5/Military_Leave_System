#!/usr/bin/env python3
"""
UPDATE examples for modifying existing data
"""

import sqlite3
from datetime import date


def update_personnel_contact():
    """Example: Update personnel contact information"""
    print("=" * 60)
    print("EXAMPLE: UPDATE PERSONNEL CONTACT INFO")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Update phone number and email
    cursor.execute('''
        UPDATE personnel 
        SET phone = ?, email = ?, updated_at = CURRENT_TIMESTAMP
        WHERE service_number = ?
    ''', ('+2348012345999', 'updated.email@test.mil.ng', 'NG/A/001'))

    conn.commit()

    print(f"✓ Updated contact info for NG/A/001")
    print(f"  New Phone: +2348012345999")
    print(f"  New Email: updated.email@test.mil.ng")

    conn.close()


def update_leave_entitlement():
    """Example: Update leave entitlement (e.g., carryover days)"""
    print("\n" + "=" * 60)
    print("EXAMPLE: UPDATE LEAVE ENTITLEMENT")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    current_year = date.today().year

    # Add carryover days from previous year
    cursor.execute('''
        UPDATE leave_entitlement 
        SET total_days_entitled = total_days_entitled + 5,
            days_remaining = days_remaining + 5,
            last_updated = CURRENT_TIMESTAMP
        WHERE personnel_id = (SELECT id FROM personnel WHERE service_number = ?)
        AND year = ?
    ''', ('NG/A/002', current_year))

    conn.commit()

    print(f"✓ Added 5 carryover days to NG/A/002 for {current_year}")

    # Display updated balance
    cursor.execute('''
        SELECT le.*, p.name 
        FROM leave_entitlement le
        JOIN personnel p ON le.personnel_id = p.id
        WHERE p.service_number = ? AND le.year = ?
    ''', ('NG/A/002', current_year))

    row = cursor.fetchone()
    if row:
        print(f"  Personnel: {row[5]} (NG/A/002)")
        print(f"  Total Entitled: {row[2]} days")
        print(f"  Days Used: {row[3]} days")
        print(f"  Days Remaining: {row[4]} days")

    conn.close()


def update_leave_request_status():
    """Example: Update leave request status (manual override)"""
    print("\n" + "=" * 60)
    print("EXAMPLE: UPDATE LEAVE REQUEST STATUS")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Find a pending request
    cursor.execute('''
        SELECT id, status FROM leave_requests 
        WHERE status = 'pending_rsm' LIMIT 1
    ''')

    row = cursor.fetchone()
    if row:
        request_id = row[0]
        old_status = row[1]

        cursor.execute('''
            UPDATE leave_requests 
            SET status = 'cancelled',
                cancelled_date = CURRENT_TIMESTAMP,
                cancellation_reason = 'Administrative cancellation',
                last_modified = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (request_id,))

        conn.commit()

        print(f"✓ Updated leave request {request_id}")
        print(f"  Old Status: {old_status}")
        print(f"  New Status: cancelled")
    else:
        print("No pending requests found to update")

    conn.close()


def update_off_duty_schedule():
    """Example: Update off-duty schedule for specific personnel"""
    print("\n" + "=" * 60)
    print("EXAMPLE: UPDATE OFF-DUTY SCHEDULE")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Change Wednesday to off-duty for a specific soldier
    cursor.execute('''
        UPDATE off_duty_schedule 
        SET is_off_duty = 1, notes = 'Religious observance'
        WHERE personnel_id = (SELECT id FROM personnel WHERE service_number = ?)
        AND day_of_week = ?
    ''', ('NG/A/003', 2))  # Wednesday = 2

    if cursor.rowcount == 0:
        # Insert if not exists
        cursor.execute('''
            INSERT INTO off_duty_schedule (personnel_id, day_of_week, is_off_duty, notes)
            SELECT id, ?, 1, 'Religious observance'
            FROM personnel WHERE service_number = ?
        ''', (2, 'NG/A/003'))

    conn.commit()

    print(f"✓ Updated off-duty schedule for NG/A/003")
    print(f"  Wednesday set as off-duty")

    conn.close()


def update_system_configuration():
    """Example: Update system configuration values"""
    print("\n" + "=" * 60)
    print("EXAMPLE: UPDATE SYSTEM CONFIGURATION")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Update maximum concurrent leave limit
    cursor.execute('''
        UPDATE system_config 
        SET config_value = '15', updated_at = CURRENT_TIMESTAMP
        WHERE config_key = 'max_people_on_leave_per_day'
    ''')

    conn.commit()

    print(f"✓ Updated system configuration")
    print(f"  max_people_on_leave_per_day: 10 → 15")

    # Display all configurations
    cursor.execute("SELECT config_key, config_value FROM system_config")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()


def update_duty_roster_assignment():
    """Example: Update duty roster assignment (reassign personnel)"""
    print("\n" + "=" * 60)
    print("EXAMPLE: UPDATE DUTY ROSTER ASSIGNMENT")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Find a duty assignment to update
    cursor.execute('''
        SELECT dr.id, dr.duty_date, dr.shift, dr.duty_type, p.name as current_personnel
        FROM duty_roster dr
        JOIN personnel p ON dr.personnel_id = p.id
        WHERE dr.duty_date >= date('now')
        LIMIT 1
    ''')

    row = cursor.fetchone()
    if row:
        duty_id = row[0]
        old_personnel = row[4]

        # Get another available personnel
        cursor.execute('''
            SELECT id, name FROM personnel 
            WHERE rank_category = 'soldier' AND is_active = 1
            AND id != (SELECT personnel_id FROM duty_roster WHERE id = ?)
            LIMIT 1
        ''', (duty_id,))

        new_personnel = cursor.fetchone()
        if new_personnel:
            cursor.execute('''
                UPDATE duty_roster 
                SET personnel_id = ?, notes = 'Reassigned due to schedule conflict',
                    assigned_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_personnel[0], duty_id))

            conn.commit()

            print(f"✓ Reassigned duty {duty_id}")
            print(f"  Old Personnel: {old_personnel}")
            print(f"  New Personnel: {new_personnel[1]}")
    else:
        print("No duty assignments found to update")

    conn.close()


def batch_update_rank():
    """Example: Batch update ranks for promotions"""
    print("\n" + "=" * 60)
    print("EXAMPLE: BATCH UPDATE RANKS (PROMOTIONS)")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Promotion mapping
    promotions = [
        ('NG/A/002', 'Corporal', 3),      # Lance Corporal → Corporal
        ('NG/A/003', 'Sergeant', 4),      # Corporal → Sergeant
        ('NG/A/004', 'Staff Sergeant', 5),  # Sergeant → Staff Sergeant
    ]

    for service_number, new_rank, new_order in promotions:
        cursor.execute('''
            UPDATE personnel 
            SET rank = ?, rank_order = ?, updated_at = CURRENT_TIMESTAMP
            WHERE service_number = ?
        ''', (new_rank, new_order, service_number))

        print(f"  {service_number}: Promoted to {new_rank}")

    conn.commit()
    print(f"✓ Processed {len(promotions)} promotions")

    conn.close()


if __name__ == "__main__":
    update_personnel_contact()
    update_leave_entitlement()
    update_leave_request_status()
    update_off_duty_schedule()
    update_system_configuration()
    update_duty_roster_assignment()
    batch_update_rank()
    print("\n" + "=" * 60)
    print("ALL UPDATE EXAMPLES COMPLETED")
    print("=" * 60)
