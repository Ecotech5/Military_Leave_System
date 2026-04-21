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