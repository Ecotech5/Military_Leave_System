<<<<<<< HEAD
# complete_system_setup.py
import sqlite3 import hashlib import os DB_PATH = 'database/military_leave_system.db' def hash_password(password): return hashlib.sha256(password.encode()).hexdigest() def setup_complete_system(): print("=" * 60) print("COMPLETE SYSTEM SETUP") print("=" * 60) # Create database directory
os.makedirs('database', exist_ok = True) # Delete existing database to start fresh
if os.path.exists(DB_PATH): os.remove(DB_PATH) print("\n✓ Removed existing database") conn = sqlite3.connect(DB_PATH) cursor = conn.cursor() # =====================================================
# CREATE ALL TABLES
# =====================================================
print("\n[1/6] Creating tables...") # Personnel table (with password and force_password_change columns)
cursor.execute(
    '''
        CREATE TABLE personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            rank TEXT NOT NULL,
            rank_category TEXT NOT NULL,
            rank_order INTEGER NOT NULL,
            unit TEXT,
            platoon TEXT,
            company TEXT,
            battalion TEXT,
            email TEXT,
            phone TEXT,
            password TEXT,
            force_password_change INTEGER DEFAULT 1,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    '''
) print("  ✓ Personnel table created") # Ranks table
cursor.execute(
    '''
        CREATE TABLE ranks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank_name TEXT UNIQUE NOT NULL,
            rank_abbreviation TEXT NOT NULL,
            rank_category TEXT NOT NULL,
            rank_order INTEGER NOT NULL,
            rank_grade TEXT
        )
    '''
) # Insert ranks
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
    ] for r in ranks: cursor.execute(
    "INSERT INTO ranks VALUES (NULL, ?, ?, ?, ?, ?)",
    r
) print("  ✓ Ranks table created with 21 ranks") # Leave entitlement table
cursor.execute(
    '''
        CREATE TABLE leave_entitlement (
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
    '''
) print("  ✓ Leave entitlement table created") # Leave requests table
cursor.execute(
    '''
        CREATE TABLE leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_days INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT ' pending_rsm ',
            rsm_approver_id INTEGER,
            rsm_approval_date DATETIME,
            rsm_recommendation TEXT,
            rsm_comments TEXT,
            ao_approver_id INTEGER,
            ao_approval_date DATETIME,
            ao_recommendation TEXT,
            ao_comments TEXT,
            commander_approver_id INTEGER,
            commander_decision_date DATETIME,
            commander_decision TEXT,
            commander_comments TEXT,
            submitted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id)
        )
    '''
) print("  ✓ Leave requests table created") # Off-duty schedule table
cursor.execute(
    '''
        CREATE TABLE off_duty_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            is_recurring BOOLEAN DEFAULT 1,
            effective_from DATE NOT NULL,
            effective_to DATE,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id)
        )
    '''
) print("  ✓ Off-duty schedule table created") # Duty roster table
cursor.execute(
    '''
        CREATE TABLE duty_roster (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            duty_date DATE NOT NULL,
            shift TEXT NOT NULL,
            duty_type TEXT NOT NULL,
            personnel_id INTEGER NOT NULL,
            assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id)
        )
    '''
) print("  ✓ Duty roster table created") # Duty types table
cursor.execute(
    '''
        CREATE TABLE duty_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            duty_name TEXT UNIQUE NOT NULL,
            duty_category TEXT NOT NULL,
            default_shift TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    '''
) duties = [
        ('Guard Duty', 'soldier_only', 'night', 1),
        ('Patrol Duty', 'soldier_only', '24hr', 1),
        ('Transport Duty', 'soldier_only', 'morning', 1),
        ('Orderly Duty', 'soldier_only', '24hr', 1),
        ('Command Duty', 'officer_only', '24hr', 1),
        ('Staff Duty', 'officer_only', 'morning', 1),
        ('Admin Duty', 'both', 'morning', 1),
        ('Signal Duty', 'both', '24hr', 1),
        ('Medical Duty', 'both', '24hr', 1),
        ('Catering Duty', 'soldier_only', 'morning', 1)
    ] for d in duties: cursor.execute(
    "INSERT INTO duty_types VALUES (NULL, ?, ?, ?, ?)",
    d
) print("  ✓ Duty types table created") # Approval rules table
cursor.execute(
    '''
        CREATE TABLE approval_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank_category TEXT NOT NULL,
            requires_rsm BOOLEAN DEFAULT 0,
            requires_ao BOOLEAN DEFAULT 1,
            requires_commander BOOLEAN DEFAULT 1
        )
    '''
) cursor.execute(
    "INSERT INTO approval_rules VALUES (NULL, 'soldier', 1, 1, 1)"
) cursor.execute(
    "INSERT INTO approval_rules VALUES (NULL, 'officer', 0, 1, 1)"
) print("  ✓ Approval rules table created") # System config table
cursor.execute(
    '''
        CREATE TABLE system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT UNIQUE NOT NULL,
            config_value TEXT,
            description TEXT
        )
    '''
) configs = [
        ('max_leave_days_per_year', '14', 'Maximum annual leave entitlement'),
        ('min_days_before_leave_notice', '7', 'Minimum days advance notice'),
        ('max_people_on_leave_per_day', '10', 'Maximum concurrent leave'),
        ('roster_generation_days_ahead', '7', 'Days to generate roster in advance')
    ] for c in configs: cursor.execute(
    "INSERT INTO system_config VALUES (NULL, ?, ?, ?)",
    c
) print("  ✓ System config table created") # =====================================================
# CREATE MASTER ADMIN (YOU)
# =====================================================
print("\n[2/6] Creating Master Admin account (YOU)...") master_password_hash = hash_password("NACWCCORPERS123456") cursor.execute(
    '''
        INSERT INTO personnel (
            service_number, name, rank, rank_category, rank_order, 
            unit, email, phone, password, force_password_change, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
        'NACWCCORPERS',
        # service_number
        'System Administrator',
        # name
        'Admin',
        # rank
        'officer',
        # rank_category
        100,
        # rank_order (highest)
        'HQ',
        # unit
        'admin@system.mil.ng',
        # email
        '08000000000',
        # phone
        master_password_hash,
        # password
        0,
        # force_password_change (0 = no)
        1 # is_active
    )
) print("  ✓ Master Admin created:") print("    Service Number: NACWCCORPERS") print("    Password: NACWCCORPERS123456") print(
    "    Role: Can add/remove personnel (backdoor access)"
) # =====================================================
# CREATE LEAVE ENTITLEMENT FOR MASTER ADMIN
# =====================================================
print(
    "\n[3/6] Creating leave entitlement for Master Admin..."
)
from datetime import datetime current_year = datetime.now().year cursor.execute(
        "SELECT id FROM personnel WHERE service_number = 'NACWCCORPERS'"
    ) admin_id = cursor.fetchone() [0] cursor.execute(
        '''
        INSERT INTO leave_entitlement (personnel_id, year, total_days_entitled, days_used, days_remaining)
        VALUES (?, ?, 14, 0, 14)
    ''',
        (admin_id, current_year)
    ) print("  ✓ Leave entitlement created (14 days)") # =====================================================
    # VERIFY SETUP
    # =====================================================
    print("\n[4/6] Verifying database...") cursor.execute("SELECT COUNT(*) FROM personnel") personnel_count = cursor.fetchone() [0] print(f "  ✓ Personnel count: {personnel_count}") cursor.execute("SELECT COUNT(*) FROM ranks") ranks_count = cursor.fetchone() [0] print(f "  ✓ Ranks count: {ranks_count}") cursor.execute("SELECT COUNT(*) FROM duty_types") duty_count = cursor.fetchone() [0] print(f "  ✓ Duty types count: {duty_count}") cursor.execute("SELECT COUNT(*) FROM approval_rules") rules_count = cursor.fetchone() [0] print(f "  ✓ Approval rules count: {rules_count}") # =====================================================
    # CREATE INDEXES
    # =====================================================
    print("\n[5/6] Creating indexes...") cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_personnel_service ON personnel(service_number)"
    ) cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_personnel_active ON personnel(is_active)"
    ) cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(status)"
    ) cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_leave_requests_dates ON leave_requests(start_date, end_date)"
    ) cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_leave_requests_personnel ON leave_requests(personnel_id)"
    ) cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_duty_roster_date ON duty_roster(duty_date)"
    ) print("  ✓ Indexes created") # =====================================================
    # CREATE VIEWS
    # =====================================================
    print("\n[6/6] Creating views...") cursor.execute(
        '''
        CREATE VIEW IF NOT EXISTS vw_pending_approvals AS
        SELECT 
            lr.id as request_id,
            p.name as requester_name,
            p.rank as requester_rank,
            p.rank_category,
            lr.start_date,
            lr.end_date,
            lr.total_days,
            lr.status
        FROM leave_requests lr
        JOIN personnel p ON lr.personnel_id = p.id
        WHERE lr.status IN (' pending_rsm ', ' pending_ao ', ' pending_commander ')
        ORDER BY lr.submitted_date ASC
    '''
    ) print("  ✓ Views created") # Commit everything
    conn.commit() conn.close() print("\n" + "=" * 60) print("SETUP COMPLETE!") print("=" * 60) print("\n" + "=" * 60) print("LOGIN CREDENTIALS") print("=" * 60) print("\nMASTER ADMIN (YOU):") print("  Service Number: NACWCCORPERS") print("  Password: NACWCCORPERS123456") print("  Permissions: Can add/remove personnel") print("\n" + "=" * 60) print("NEXT STEPS") print("=" * 60) print("\n1. Run: python app.py") print(
        "2. Login with: NACWCCORPERS / NACWCCORPERS123456"
    ) print("3. Add personnel through the web interface") print(
        "   - Default password for new users: NACWC123456"
    ) print("   - They MUST change password on first login") print("\n" + "=" * 60) print("HOW TO ADD NEW PERSONNEL") print("=" * 60) print("\nAfter logging in as Master Admin:") print("1. Click 'Add Personnel' in the navigation bar") print("2. Fill in their details") print("3. Default password will be: NACWC123456") print(
        "4. They will be forced to change password on first login"
    ) if __name__ == "__main__": setup_complete_system()
=======
-- Nigerian Army Leave & Duty Roster Management System
-- Complete Database Schema
-- Personnel and Ranks Tables
CREATE TABLE ranks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rank_name TEXT NOT NULL UNIQUE,
    rank_abbreviation TEXT NOT NULL,
    rank_category TEXT CHECK(rank_category IN ('soldier', 'officer')),
    rank_order INTEGER NOT NULL,
    nato_code TEXT
);
CREATE TABLE personnel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_number TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    rank TEXT NOT NULL,
    rank_category TEXT CHECK(rank_category IN ('soldier', 'officer')),
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rank) REFERENCES ranks(rank_name)
);
-- Leave Management Tables
CREATE TABLE leave_entitlement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    total_days_entitled INTEGER DEFAULT 14,
    days_used INTEGER DEFAULT 0,
    days_remaining INTEGER DEFAULT 14,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(personnel_id, year),
    FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE
);
CREATE TABLE leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_id INTEGER NOT NULL,
    leave_type TEXT CHECK(
        leave_type IN (
            'annual',
            'sick',
            'compassionate',
            'study',
            'maternity',
            'paternity'
        )
    ),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    reason TEXT,
    status TEXT CHECK(
        status IN (
            'pending_rsm',
            'pending_ao',
            'pending_commander',
            'approved',
            'rejected',
            'cancelled'
        )
    ),
    -- RSM approval (soldiers only)
    rsm_approver_id INTEGER,
    rsm_approval_date DATETIME,
    rsm_recommendation TEXT CHECK(
        rsm_recommendation IN ('recommend', 'do_not_recommend')
    ),
    rsm_comments TEXT,
    -- Admin Officer approval (EVERYONE)
    ao_approver_id INTEGER,
    ao_approval_date DATETIME,
    ao_recommendation TEXT CHECK(
        ao_recommendation IN ('recommend', 'do_not_recommend')
    ),
    ao_comments TEXT,
    -- Commander final decision (EVERYONE)
    commander_approver_id INTEGER,
    commander_decision_date DATETIME,
    commander_decision TEXT CHECK(commander_decision IN ('approved', 'rejected')),
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
);
-- Off-Duty Schedule Tables
CREATE TABLE off_duty_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_id INTEGER NOT NULL,
    day_of_week INTEGER CHECK(
        day_of_week BETWEEN 0 AND 6
    ),
    -- 0=Monday, 6=Sunday
    is_off_duty BOOLEAN DEFAULT 1,
    notes TEXT,
    FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
    UNIQUE(personnel_id, day_of_week)
);
CREATE TABLE off_duty_exceptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_id INTEGER NOT NULL,
    exception_date DATE NOT NULL,
    is_off_duty BOOLEAN DEFAULT 1,
    reason TEXT,
    approved_by INTEGER,
    approved_date DATETIME,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (personnel_id) REFERENCES personnel(id),
    FOREIGN KEY (approved_by) REFERENCES personnel(id)
);
-- Duty Roster Tables
CREATE TABLE duty_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    duty_name TEXT NOT NULL UNIQUE,
    category TEXT CHECK(
        category IN ('soldier_only', 'officer_only', 'both')
    ),
    default_shift TEXT CHECK(
        default_shift IN ('morning', 'evening', 'night', '24hr')
    ),
    requires_supervisor BOOLEAN DEFAULT 0,
    description TEXT
);
CREATE TABLE duty_roster (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    duty_date DATE NOT NULL,
    shift TEXT CHECK(shift IN ('morning', 'evening', 'night', '24hr')),
    duty_type TEXT NOT NULL,
    personnel_id INTEGER NOT NULL,
    assigned_by INTEGER NOT NULL,
    assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    is_standby BOOLEAN DEFAULT 0,
    FOREIGN KEY (duty_type) REFERENCES duty_types(duty_name),
    FOREIGN KEY (personnel_id) REFERENCES personnel(id),
    FOREIGN KEY (assigned_by) REFERENCES personnel(id)
);
-- Workflow and Configuration Tables
CREATE TABLE approval_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rank_category TEXT NOT NULL CHECK(rank_category IN ('soldier', 'officer')),
    requires_rsm BOOLEAN DEFAULT 0,
    requires_ao BOOLEAN DEFAULT 1,
    requires_commander BOOLEAN DEFAULT 1,
    approval_order INTEGER
);
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE notification_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_id INTEGER NOT NULL,
    notification_type TEXT CHECK(notification_type IN ('email', 'sms')),
    subject TEXT,
    message TEXT,
    sent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'sent',
    FOREIGN KEY (personnel_id) REFERENCES personnel(id)
);
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    table_name TEXT,
    record_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES personnel(id)
);
-- Indexes for Performance
CREATE INDEX idx_personnel_service_number ON personnel(service_number);
CREATE INDEX idx_personnel_rank_category ON personnel(rank_category);
CREATE INDEX idx_leave_requests_personnel ON leave_requests(personnel_id);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);
CREATE INDEX idx_leave_requests_dates ON leave_requests(start_date, end_date);
CREATE INDEX idx_leave_entitlement_personnel_year ON leave_entitlement(personnel_id, year);
CREATE INDEX idx_duty_roster_date ON duty_roster(duty_date);
CREATE INDEX idx_duty_roster_personnel ON duty_roster(personnel_id);
CREATE INDEX idx_off_duty_schedule_personnel ON off_duty_schedule(personnel_id);
CREATE INDEX idx_off_duty_exceptions_date ON off_duty_exceptions(exception_date);
-- Views for Common Queries
CREATE VIEW vw_pending_approvals AS
SELECT lr.id as request_id,
    p.service_number,
    p.name,
    p.rank,
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
        ELSE 'No Action Required'
    END as required_approver
FROM leave_requests lr
    JOIN personnel p ON lr.personnel_id = p.id
WHERE lr.status IN ('pending_rsm', 'pending_ao', 'pending_commander')
ORDER BY lr.submitted_date;
CREATE VIEW vw_available_personnel AS
SELECT p.id,
    p.service_number,
    p.name,
    p.rank,
    p.rank_category,
    CURRENT_DATE as check_date,
    CASE
        WHEN lr.id IS NOT NULL THEN 'On Leave'
        WHEN ods.id IS NOT NULL THEN 'Off Duty'
        ELSE 'Available'
    END as availability_status
FROM personnel p
    LEFT JOIN leave_requests lr ON p.id = lr.personnel_id
    AND lr.status = 'approved'
    AND CURRENT_DATE BETWEEN lr.start_date AND lr.end_date
    LEFT JOIN off_duty_schedule ods ON p.id = ods.personnel_id
    AND ods.day_of_week = CAST(strftime('%w', CURRENT_DATE) AS INTEGER)
WHERE p.is_active = 1;
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
