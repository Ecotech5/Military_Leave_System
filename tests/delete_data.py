#!/usr/bin/env python3
"""
DELETE examples with safety checks for removing data
"""

import sqlite3


def safe_delete_with_check(table, condition, params, description):
    """Safe delete with foreign key check"""
    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # First check if there are dependent records
    dependent_checks = {
        'personnel': [
            ("leave_requests", "personnel_id"),
            ("leave_entitlement", "personnel_id"),
            ("off_duty_schedule", "personnel_id"),
            ("duty_roster", "personnel_id")
        ],
        'leave_requests': [
            ("audit_log", "record_id", "table_name = 'leave_requests'")
        ]
    }

    if table in dependent_checks:
        print(f"\n⚠ WARNING: Deleting from '{table}' may affect other tables!")
        for dep_table, fk_column, *extra in dependent_checks[table]:
            if extra:
                extra_condition = extra[0]
                cursor.execute(
                    f"SELECT COUNT(*) FROM {dep_table} WHERE {fk_column} = ? AND {extra_condition}", params)
            else:
                cursor.execute(
                    f"SELECT COUNT(*) FROM {dep_table} WHERE {fk_column} = ?", params)
            count = cursor.fetchone()[0]
            if count > 0:
                print(
                    f"  → {count} record(s) in '{dep_table}' will be affected")

        response = input("\n  Continue with deletion? (yes/no): ")
        if response.lower() != 'yes':
            print("  Deletion cancelled.")
            conn.close()
            return False

    # Perform the deletion
    cursor.execute(f"DELETE FROM {table} WHERE {condition}", params)
    deleted_count = cursor.rowcount
    conn.commit()

    print(f"✓ Deleted {deleted_count} record(s) from {table}")
    conn.close()
    return True


def delete_cancelled_leave_request():
    """Example: Delete a cancelled leave request"""
    print("=" * 60)
    print("EXAMPLE: DELETE CANCELLED LEAVE REQUEST")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Find a cancelled request
    cursor.execute('''
        SELECT id, status, cancellation_reason 
        FROM leave_requests 
        WHERE status = 'cancelled' 
        LIMIT 1
    ''')

    row = cursor.fetchone()
    conn.close()

    if row:
        request_id = row[0]
        print(f"Found cancelled request ID: {request_id}")
        print(f"  Cancellation Reason: {row[2]}")

        safe_delete_with_check('leave_requests', 'id = ?', (request_id,),
                               f"Delete cancelled leave request {request_id}")
    else:
        print("No cancelled leave requests found to delete")


def delete_off_duty_exception():
    """Example: Delete an off-duty exception"""
    print("\n" + "=" * 60)
    print("EXAMPLE: DELETE OFF-DUTY EXCEPTION")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Find a pending off-duty exception
    cursor.execute('''
        SELECT id, personnel_id, exception_date, reason 
        FROM off_duty_exceptions 
        WHERE status = 'pending'
        LIMIT 1
    ''')

    row = cursor.fetchone()
    conn.close()

    if row:
        exception_id = row[0]
        print(f"Found off-duty exception ID: {exception_id}")
        print(f"  Date: {row[2]}")
        print(f"  Reason: {row[3]}")

        conn = sqlite3.connect("military_leave_system.db")
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM off_duty_exceptions WHERE id = ?", (exception_id,))
        conn.commit()

        print(f"✓ Deleted off-duty exception {exception_id}")
        conn.close()
    else:
        print("No pending off-duty exceptions found to delete")


def delete_duty_roster_assignments():
    """Example: Delete duty roster assignments for a specific date range"""
    print("\n" + "=" * 60)
    print("EXAMPLE: DELETE DUTY ROSTER ASSIGNMENTS")
    print("=" * 60)

    from datetime import date, timedelta

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Delete rosters older than 30 days
    cutoff_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')

    cursor.execute('''
        SELECT COUNT(*) as count FROM duty_roster 
        WHERE duty_date < ?
    ''', (cutoff_date,))

    count = cursor.fetchone()[0]

    if count > 0:
        print(f"Found {count} duty roster entries older than {cutoff_date}")
        response = input(f"  Delete {count} old roster entries? (yes/no): ")

        if response.lower() == 'yes':
            cursor.execute(
                "DELETE FROM duty_roster WHERE duty_date < ?", (cutoff_date,))
            deleted = cursor.rowcount
            conn.commit()
            print(f"✓ Deleted {deleted} old duty roster entries")
        else:
            print("  Deletion cancelled.")
    else:
        print("No old duty roster entries found to delete")

    conn.close()


def delete_inactive_personnel():
    """Example: Delete inactive personnel (with safety checks)"""
    print("\n" + "=" * 60)
    print("EXAMPLE: DELETE INACTIVE PERSONNEL")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Find inactive personnel
    cursor.execute('''
        SELECT id, service_number, name, rank 
        FROM personnel 
        WHERE is_active = 0
    ''')

    inactive = cursor.fetchall()
    conn.close()

    if inactive:
        print(f"Found {len(inactive)} inactive personnel:")
        for person in inactive:
            print(f"  • {person[1]}: {person[2]} ({person[3]})")

        response = input("\n  Delete these inactive personnel? (yes/no): ")

        if response.lower() == 'yes':
            for person in inactive:
                personnel_id = person[0]
                safe_delete_with_check('personnel', 'id = ?', (personnel_id,),
                                       f"Delete inactive personnel {person[1]}")
        else:
            print("  Deletion cancelled.")
    else:
        print("No inactive personnel found to delete")


def delete_old_notifications():
    """Example: Delete old notification logs"""
    print("\n" + "=" * 60)
    print("EXAMPLE: DELETE OLD NOTIFICATION LOGS")
    print("=" * 60)

    from datetime import date, timedelta

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Delete notifications older than 90 days
    cutoff_date = (date.today() - timedelta(days=90)).strftime('%Y-%m-%d')

    cursor.execute('''
        SELECT COUNT(*) as count FROM notification_log 
        WHERE date(sent_date) < ?
    ''', (cutoff_date,))

    count = cursor.fetchone()[0]

    if count > 0:
        cursor.execute(
            "DELETE FROM notification_log WHERE date(sent_date) < ?", (cutoff_date,))
        deleted = cursor.rowcount
        conn.commit()
        print(
            f"✓ Deleted {deleted} old notification logs (older than {cutoff_date})")
    else:
        print("No old notification logs found to delete")

    conn.close()


def delete_audit_logs():
    """Example: Delete old audit logs (with caution)"""
    print("\n" + "=" * 60)
    print("EXAMPLE: DELETE OLD AUDIT LOGS")
    print("=" * 60)

    from datetime import date, timedelta

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Delete audit logs older than 1 year
    cutoff_date = (date.today() - timedelta(days=365)).strftime('%Y-%m-%d')

    cursor.execute('''
        SELECT COUNT(*) as count FROM audit_log 
        WHERE date(timestamp) < ?
    ''', (cutoff_date,))

    count = cursor.fetchone()[0]

    if count > 0:
        print(f"⚠ WARNING: Deleting audit logs removes security trail!")
        print(f"  Found {count} audit logs older than {cutoff_date}")

        response = input("  Delete these old audit logs? (yes/no): ")

        if response.lower() == 'yes':
            cursor.execute(
                "DELETE FROM audit_log WHERE date(timestamp) < ?", (cutoff_date,))
            deleted = cursor.rowcount
            conn.commit()
            print(f"✓ Deleted {deleted} old audit logs")
        else:
            print("  Deletion cancelled.")
    else:
        print("No old audit logs found to delete")

    conn.close()


def delete_duplicate_off_duty_entries():
    """Example: Delete duplicate off-duty schedule entries"""
    print("\n" + "=" * 60)
    print("EXAMPLE: DELETE DUPLICATE OFF-DUTY ENTRIES")
    print("=" * 60)

    conn = sqlite3.connect("military_leave_system.db")
    cursor = conn.cursor()

    # Find duplicates
    cursor.execute('''
        SELECT personnel_id, day_of_week, COUNT(*) as count
        FROM off_duty_schedule
        GROUP BY personnel_id, day_of_week
        HAVING COUNT(*) > 1
    ''')

    duplicates = cursor.fetchall()

    if duplicates:
        print(f"Found duplicate entries for {len(duplicates)} combinations")

        for dup in duplicates:
            personnel_id, day_of_week, count = dup

            # Keep the first one, delete others
            cursor.execute('''
                DELETE FROM off_duty_schedule 
                WHERE personnel_id = ? AND day_of_week = ?
                AND id NOT IN (
                    SELECT MIN(id) FROM off_duty_schedule 
                    WHERE personnel_id = ? AND day_of_week = ?
                )
            ''', (personnel_id, day_of_week, personnel_id, day_of_week))

            deleted = cursor.rowcount
            print(
                f"  Deleted {deleted} duplicate entries for personnel {personnel_id}, day {day_of_week}")

        conn.commit()
    else:
        print("No duplicate off-duty entries found")

    conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("DELETE EXAMPLES WITH SAFETY CHECKS")
    print("=" * 60)
    print("\nNOTE: These operations modify the database.")
    print("All deletions include safety checks and confirmations.\n")

    delete_cancelled_leave_request()
    delete_off_duty_exception()
    delete_duty_roster_assignments()
    delete_inactive_personnel()
    delete_old_notifications()
    delete_audit_logs()
    delete_duplicate_off_duty_entries()

    print("\n" + "=" * 60)
    print("ALL DELETE EXAMPLES COMPLETED")
    print("=" * 60)
