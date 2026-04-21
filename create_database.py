#!/usr/bin/env python3
"""
Nigerian Army Leave Management System - Clean Database Creator
Creates ONLY the database structure (tables, indexes, views)
NO sample data - ready to accept real inputs later
"""

import sqlite3
import os

# Database path
DB_PATH = 'database/military_leave_system.db'


def create_clean_database():
    """Create database structure ONLY - no sample personnel data"""

    print("=" * 70)
    print("NIGERIAN ARMY LEAVE MANAGEMENT SYSTEM")
    print("Clean Database Creator (Structure Only)")
    print("=" * 70)

    # Create database directory if it doesn't exist
    if not os.path.exists('database'):
        os.makedirs('database')
        print("\n[OK] Created database folder")

    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("\n[OK] Removed existing database")

    print("\n[1/3] Creating database structure...")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    create_tables(cursor)

    # Create indexes
    create_indexes(cursor)

    # Create views
    create_views(cursor)

    # Create triggers
    create_triggers(cursor)

    print("    [OK] 12 tables created")
    print("    [OK] Indexes created")
    print("    [OK] Views created")
    print("    [OK] Triggers created")

    print("\n[2/3] Inserting reference data...")

    # Insert reference data
    insert_ranks(cursor)
    insert_duty_types(cursor)
    insert_approval_rules(cursor)
    insert_system_config(cursor)

    # Count reference data
    cursor.execute("SELECT COUNT(*) FROM ranks")
    rank_count = cursor.fetchone()[0]
    print(f"    [OK] {rank_count} Nigerian Army ranks loaded")

    cursor.execute("SELECT COUNT(*) FROM duty_types")
    duty_count = cursor.fetchone()[0]
    print(f"    [OK] {duty_count} duty types loaded")

    cursor.execute("SELECT COUNT(*) FROM approval_rules")
    rule_count = cursor.fetchone()[0]
    print(f"    [OK] {rule_count} approval rules loaded")

    cursor.execute("SELECT COUNT(*) FROM system_config")
    config_count = cursor.fetchone()[0]
    print(f"    [OK] {config_count} system configurations loaded")

    # Verify no personnel data
    cursor.execute("SELECT COUNT(*) FROM personnel")
    personnel_count = cursor.fetchone()[0]
    print(
        f"\n    [INFO] Personnel records: {personnel_count} (ready for input)")

    cursor.execute("SELECT COUNT(*) FROM leave_requests")
    leave_count = cursor.fetchone()[0]
    print(f"    [INFO] Leave requests: {leave_count} (ready for input)")

    # Commit and close
    conn.commit()
    conn.close()

    print("\n[3/3] Database ready!")

    print("\n" + "=" * 70)
    print("DATABASE CREATED SUCCESSFULLY!")
    print("=" * 70)

    # Get file size
    file_size = os.path.getsize(DB_PATH)
    print(f"\nDatabase location: {DB_PATH}")
    print(f"Database size: {file_size:,} bytes")

    print("\n" + "=" * 70)
    print("WHAT'S IN THE DATABASE:")
    print("=" * 70)
    print("  [OK] 12 Tables (structure only)")
    print("  [OK] Nigerian Army Ranks (reference data)")
    print("  [OK] Duty Types (reference data)")
    print("  [OK] Approval Rules (configuration)")
    print("  [OK] System Settings (configuration)")
    print("  [OK] Indexes for performance")
    print("  [OK] Views for common queries")
    print("  [OK] Triggers for automation")
    print("")
    print("  [EMPTY] NO personnel data (you will add this)")
    print("  [EMPTY] NO leave requests (you will add this)")
    print("  [EMPTY] NO duty rosters (system will generate)")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("  1. Run 'python app.py' to start the web interface")
    print("  2. Use the web form to add personnel")
    print("  3. Submit leave requests through the system")
    print("  4. Approve/reject as RSM, AO, or Commander")
    print("  5. Generate duty rosters")

    return True


def create_tables(cursor):
    """Create all database tables"""

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            rank TEXT NOT NULL,
            rank_category TEXT NOT NULL CHECK(rank_category IN ('soldier', 'officer')),
            rank_order INTEGER NOT NULL,
            unit TEXT,
            platoon TEXT,
            company TEXT,
            battalion TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            date_of_birth DATE,
            date_of_enlistment DATE,
            date_of_commission DATE,
            next_of_kin TEXT,
            next_of_kin_phone TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ranks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank_name TEXT UNIQUE NOT NULL,
            rank_abbreviation TEXT NOT NULL,
            rank_category TEXT NOT NULL CHECK(rank_category IN ('soldier', 'officer')),
            rank_order INTEGER NOT NULL,
            rank_grade TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_entitlement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            total_days_entitled INTEGER DEFAULT 14,
            days_used INTEGER DEFAULT 0,
            days_remaining INTEGER DEFAULT 14,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
            UNIQUE(personnel_id, year)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL CHECK(leave_type IN ('annual', 'sick', 'compassionate', 'study', 'maternity', 'paternity')),
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_days INTEGER NOT NULL,
            reason TEXT,
            status TEXT NOT NULL DEFAULT 'pending_rsm',
            rsm_approver_id INTEGER,
            rsm_approval_date DATETIME,
            rsm_recommendation TEXT CHECK(rsm_recommendation IN ('recommend', 'do_not_recommend', NULL)),
            rsm_comments TEXT,
            ao_approver_id INTEGER,
            ao_approval_date DATETIME,
            ao_recommendation TEXT CHECK(ao_recommendation IN ('recommend', 'do_not_recommend', NULL)),
            ao_comments TEXT,
            commander_approver_id INTEGER,
            commander_decision_date DATETIME,
            commander_decision TEXT CHECK(commander_decision IN ('approved', 'rejected', NULL)),
            commander_comments TEXT,
            submitted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
            cancelled_date DATETIME,
            cancelled_by INTEGER,
            cancellation_reason TEXT,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id),
            FOREIGN KEY (rsm_approver_id) REFERENCES personnel(id),
            FOREIGN KEY (ao_approver_id) REFERENCES personnel(id),
            FOREIGN KEY (commander_approver_id) REFERENCES personnel(id),
            FOREIGN KEY (cancelled_by) REFERENCES personnel(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS off_duty_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL CHECK(day_of_week BETWEEN 0 AND 6),
            is_recurring BOOLEAN DEFAULT 1,
            effective_from DATE NOT NULL,
            effective_to DATE,
            notes TEXT,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id),
            FOREIGN KEY (created_by) REFERENCES personnel(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS off_duty_exceptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER NOT NULL,
            exception_date DATE NOT NULL,
            is_off_duty BOOLEAN NOT NULL,
            reason TEXT,
            approved_by INTEGER,
            approved_date DATETIME,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id),
            FOREIGN KEY (approved_by) REFERENCES personnel(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS duty_roster (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            duty_date DATE NOT NULL,
            shift TEXT NOT NULL CHECK(shift IN ('morning', 'evening', 'night', '24hr')),
            duty_type TEXT NOT NULL CHECK(duty_type IN (
                'guard', 'patrol', 'transport', 'orderly', 'command', 
                'staff', 'admin', 'signal', 'medical', 'catering'
            )),
            personnel_id INTEGER NOT NULL,
            assigned_by INTEGER,
            assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            is_standby BOOLEAN DEFAULT 0,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id),
            FOREIGN KEY (assigned_by) REFERENCES personnel(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS duty_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            duty_name TEXT UNIQUE NOT NULL,
            duty_category TEXT CHECK(duty_category IN ('soldier_only', 'officer_only', 'both')),
            default_shift TEXT,
            requires_supervisor BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS approval_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank_category TEXT NOT NULL CHECK(rank_category IN ('soldier', 'officer')),
            leave_type TEXT,
            requires_rsm BOOLEAN DEFAULT 0,
            requires_ao BOOLEAN DEFAULT 1,
            requires_commander BOOLEAN DEFAULT 1,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_id INTEGER NOT NULL,
            notification_type TEXT NOT NULL CHECK(notification_type IN ('email', 'sms', 'in_app')),
            subject TEXT,
            message TEXT,
            related_entity_type TEXT,
            related_entity_id INTEGER,
            status TEXT DEFAULT 'pending',
            sent_at DATETIME,
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipient_id) REFERENCES personnel(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES personnel(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT UNIQUE NOT NULL,
            config_value TEXT,
            description TEXT,
            updated_by INTEGER,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')


def create_indexes(cursor):
    """Create indexes for performance"""

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_personnel_service_number ON personnel(service_number)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_personnel_rank_category ON personnel(rank_category)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_personnel_unit ON personnel(unit)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_personnel_active ON personnel(is_active)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_leave_requests_personnel ON leave_requests(personnel_id)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(status)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_leave_requests_dates ON leave_requests(start_date, end_date)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_duty_roster_date ON duty_roster(duty_date)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_duty_roster_personnel ON duty_roster(personnel_id)")


def create_views(cursor):
    """Create views for common queries"""

    cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_pending_approvals AS
        SELECT 
            lr.id as request_id,
            p.name as requester_name,
            p.rank as requester_rank,
            p.rank_category,
            lr.leave_type,
            lr.start_date,
            lr.end_date,
            lr.total_days,
            lr.status,
            CASE 
                WHEN lr.status = 'pending_rsm' THEN 'RSM'
                WHEN lr.status = 'pending_ao' THEN 'Admin Officer'
                WHEN lr.status = 'pending_commander' THEN 'Commander'
                ELSE NULL
            END as current_approver_role
        FROM leave_requests lr
        JOIN personnel p ON lr.personnel_id = p.id
        WHERE lr.status IN ('pending_rsm', 'pending_ao', 'pending_commander')
        ORDER BY lr.submitted_date ASC
    ''')

    cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_available_personnel AS
        SELECT 
            p.id,
            p.name,
            p.rank,
            p.rank_category,
            p.unit,
            CASE 
                WHEN lr.id IS NOT NULL AND lr.status = 'approved' AND date('now') BETWEEN lr.start_date AND lr.end_date THEN 'On Leave'
                WHEN ods.id IS NOT NULL AND (strftime('%w', 'now') = ods.day_of_week) THEN 'Off-Duty'
                ELSE 'Available'
            END as availability_status
        FROM personnel p
        LEFT JOIN leave_requests lr ON p.id = lr.personnel_id 
            AND lr.status = 'approved' 
            AND date('now') BETWEEN lr.start_date AND lr.end_date
        LEFT JOIN off_duty_schedule ods ON p.id = ods.personnel_id 
            AND ods.is_recurring = 1
            AND (ods.effective_to IS NULL OR date('now') <= ods.effective_to)
        WHERE p.is_active = 1
    ''')


def create_triggers(cursor):
    """Create triggers for automatic updates"""

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_personnel_timestamp 
        AFTER UPDATE ON personnel
        BEGIN
            UPDATE personnel SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_leave_requests_timestamp 
        AFTER UPDATE ON leave_requests
        BEGIN
            UPDATE leave_requests SET last_modified = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    ''')


def insert_ranks(cursor):
    """Insert Nigerian Army ranks"""

    ranks = [
        ('Private', 'Pte', 'soldier', 1, 'OR-1'),
        ('Lance Corporal', 'LCpl', 'soldier', 2, 'OR-2'),
        ('Corporal', 'Cpl', 'soldier', 3, 'OR-3'),
        ('Sergeant', 'Sgt', 'soldier', 4, 'OR-4'),
        ('Staff Sergeant', 'SSgt', 'soldier', 5, 'OR-5'),
        ('Warrant Officer', 'WO', 'soldier', 6, 'OR-6'),
        ('Master Warrant Officer', 'MWO', 'soldier', 7, 'OR-7'),
        ('Army Warrant Officer', 'AWO', 'soldier', 8, 'OR-8'),
        ('RSM', 'RSM', 'soldier', 9, 'OR-9'),
        ('Second Lieutenant', '2Lt', 'officer', 1, 'OF-1'),
        ('Lieutenant', 'Lt', 'officer', 2, 'OF-1'),
        ('Captain', 'Capt', 'officer', 3, 'OF-2'),
        ('Major', 'Maj', 'officer', 4, 'OF-3'),
        ('Lieutenant Colonel', 'Lt Col', 'officer', 5, 'OF-4'),
        ('Colonel', 'Col', 'officer', 6, 'OF-5'),
        ('Brigadier General', 'Brig Gen', 'officer', 7, 'OF-6'),
        ('Major General', 'Maj Gen', 'officer', 8, 'OF-7'),
        ('Lieutenant General', 'Lt Gen', 'officer', 9, 'OF-8'),
        ('General', 'Gen', 'officer', 10, 'OF-9'),
        ('Admin Officer', 'AO', 'officer', 11, 'OF-3')
    ]

    for rank in ranks:
        cursor.execute('''
            INSERT OR IGNORE INTO ranks (rank_name, rank_abbreviation, rank_category, rank_order, rank_grade)
            VALUES (?, ?, ?, ?, ?)
        ''', rank)


def insert_duty_types(cursor):
    """Insert duty types"""

    duties = [
        ('Guard Duty', 'soldier_only', 'night', 0),
        ('Patrol Duty', 'soldier_only', '24hr', 1),
        ('Transport Duty', 'soldier_only', 'morning', 0),
        ('Orderly Duty', 'soldier_only', '24hr', 0),
        ('Command Duty', 'officer_only', '24hr', 0),
        ('Staff Duty', 'officer_only', 'morning', 0),
        ('Admin Duty', 'both', 'morning', 0),
        ('Signal Duty', 'both', '24hr', 0),
        ('Medical Duty', 'both', '24hr', 0),
        ('Catering Duty', 'soldier_only', 'morning', 0)
    ]

    for duty in duties:
        cursor.execute('''
            INSERT OR IGNORE INTO duty_types (duty_name, duty_category, default_shift, requires_supervisor)
            VALUES (?, ?, ?, ?)
        ''', duty)


def insert_approval_rules(cursor):
    """Insert approval workflow rules"""

    cursor.execute('''
        INSERT OR IGNORE INTO approval_rules (rank_category, requires_rsm, requires_ao, requires_commander)
        VALUES ('soldier', 1, 1, 1)
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO approval_rules (rank_category, requires_rsm, requires_ao, requires_commander)
        VALUES ('officer', 0, 1, 1)
    ''')


def insert_system_config(cursor):
    """Insert system configuration"""

    configs = [
        ('max_leave_days_per_year', '14', 'Maximum annual leave entitlement'),
        ('min_days_before_leave_notice', '7',
         'Minimum days advance notice for leave request'),
        ('max_people_on_leave_per_day', '10',
         'Maximum number of personnel allowed on leave per day'),
        ('roster_generation_days_ahead', '7',
         'How many days in advance to generate duty roster'),
        ('email_notifications_enabled', 'true', 'Enable email notifications'),
        ('sms_notifications_enabled', 'false', 'Enable SMS notifications')
    ]

    for config in configs:
        cursor.execute('''
            INSERT OR IGNORE INTO system_config (config_key, config_value, description)
            VALUES (?, ?, ?)
        ''', config)


def show_help():
    """Show help for adding data later"""
    print("\n" + "=" * 70)
    print("HOW TO ADD PERSONNEL LATER:")
    print("=" * 70)
    print("")
    print("Option 1: Through Web Interface (Easiest)")
    print("    - Run 'python app.py'")
    print("    - Use the Add Personnel form")
    print("")
    print("Option 2: Through Python Script")
    print("    from leave_management import LeaveManager")
    print("    manager = LeaveManager()")
    print("    manager.cursor.execute(")
    print('        """')
    print('        INSERT INTO personnel (service_number, name, rank, rank_category, rank_order, unit)')
    print('        VALUES (?, ?, ?, ?, ?, ?)')
    print('        """, ("NG/A/001", "John Doe", "Private", "soldier", 1, "Alpha Company"))')
    print("    manager.conn.commit()")
    print("")
    print("Option 3: Through SQL directly")
    print("    INSERT INTO personnel (service_number, name, rank, rank_category, rank_order)")
    print("    VALUES ('NG/A/001', 'John Doe', 'Private', 'soldier', 1);")


if __name__ == "__main__":
    create_clean_database()
    show_help()
