#!/usr/bin/env python3
"""
Nigerian Army Leave Management System - Core Business Logic
<<<<<<< HEAD
With Password Authentication & Force Password Change
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
=======
Handles all leave requests, approvals, and duty roster generation
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018

DB_PATH = 'database/military_leave_system.db'


class LeaveManager:
<<<<<<< HEAD
    """Main class for managing leave requests, approvals, and duty roster"""

    def __init__(self, db_path: str = DB_PATH):
=======
    """Main class for managing leave requests and duty rosters"""

    def __init__(self, db_path: str = DB_PATH):
        """Initialize database connection"""
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

<<<<<<< HEAD
    # =====================================================
    # PASSWORD MANAGEMENT
    # =====================================================

    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return self.hash_password(plain_password) == hashed_password

    def authenticate_user(self, service_number: str, password: str) -> Optional[Dict]:
        """Authenticate a user by service number and password"""
        hashed = self.hash_password(password)
        self.cursor.execute("""
            SELECT id, name, rank, rank_category, service_number, password, force_password_change, unit
            FROM personnel 
            WHERE service_number = ? AND is_active = 1
        """, (service_number,))
        user = self.cursor.fetchone()

        if user and user['password'] == hashed:
            return dict(user)
        return None

    def change_password(self, personnel_id: int, current_password: str, new_password: str) -> Dict:
        """Change user's password and turn off force_password_change flag"""
        self.cursor.execute(
            "SELECT password FROM personnel WHERE id = ?", (personnel_id,))
        result = self.cursor.fetchone()

        if not result:
            return {"success": False, "error": "User not found"}

        if not self.verify_password(current_password, result['password']):
            return {"success": False, "error": "Current password is incorrect"}

        if len(new_password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}

        hashed_new = self.hash_password(new_password)
        self.cursor.execute("""
            UPDATE personnel 
            SET password = ?, force_password_change = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (hashed_new, personnel_id))

        self.conn.commit()
        return {"success": True, "message": "Password changed successfully"}

    def needs_password_change(self, personnel_id: int) -> bool:
        """Check if user needs to change their password"""
        self.cursor.execute(
            "SELECT force_password_change FROM personnel WHERE id = ?", (personnel_id,))
        result = self.cursor.fetchone()
        return result['force_password_change'] == 1 if result else False

    def can_add_personnel(self, service_number: str) -> bool:
        """Check if user has permission to add personnel"""
        self.cursor.execute("""
            SELECT rank FROM personnel WHERE service_number = ? AND is_active = 1
        """, (service_number,))
        result = self.cursor.fetchone()

        if not result:
            return False

        rank = result['rank']
        # Allowed roles: Master Admin, Admin Officer, Chief of Staff, Commander (Lt Col and above)
        allowed_ranks = ['Admin Officer', 'Chief of Staff',
                         'Lieutenant Colonel', 'Colonel', 'Brigadier General', 'Major General']

        # Master admin (special service number)
        if service_number == 'NACWCCORPERS':
            return True

        return rank in allowed_ranks

    # =====================================================
    # PERSONNEL MANAGEMENT
    # =====================================================
=======
    def calculate_days(self, start_date: str, end_date: str) -> int:
        """Calculate number of days between two dates (inclusive)"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return (end - start).days + 1
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018

    def get_personnel_info(self, service_number: str) -> Optional[Dict]:
        """Get personnel information by service number"""
        self.cursor.execute("""
<<<<<<< HEAD
            SELECT id, name, rank, rank_category, email, phone, unit, service_number, force_password_change
=======
            SELECT id, name, rank, rank_category, email, phone, unit
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
            FROM personnel 
            WHERE service_number = ? AND is_active = 1
        """, (service_number,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_personnel_by_id(self, personnel_id: int) -> Optional[Dict]:
        """Get personnel information by ID"""
        self.cursor.execute("""
<<<<<<< HEAD
            SELECT id, name, rank, rank_category, service_number, email, phone, force_password_change
=======
            SELECT id, name, rank, rank_category, service_number, email, phone
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
            FROM personnel 
            WHERE id = ? AND is_active = 1
        """, (personnel_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_personnel(self, category: str = None) -> List[Dict]:
<<<<<<< HEAD
        """Get all personnel, optionally filtered by category (excludes master admin)"""
=======
        """Get all personnel, optionally filtered by category"""
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        if category:
            self.cursor.execute("""
                SELECT id, service_number, name, rank, rank_category, unit, phone, email
                FROM personnel 
<<<<<<< HEAD
                WHERE rank_category = ? AND is_active = 1 AND service_number != 'NACWCCORPERS'
=======
                WHERE rank_category = ? AND is_active = 1
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
                ORDER BY rank_order
            """, (category,))
        else:
            self.cursor.execute("""
                SELECT id, service_number, name, rank, rank_category, unit, phone, email
                FROM personnel 
<<<<<<< HEAD
                WHERE is_active = 1 AND service_number != 'NACWCCORPERS'
                ORDER BY rank_category, rank_order
            """)
        return [dict(row) for row in self.cursor.fetchall()]

    def add_personnel(self, service_number: str, name: str, rank: str, rank_category: str,
                      rank_order: int, unit: str = None, platoon: str = None,
                      email: str = None, phone: str = None) -> Dict:
        """Add new personnel to the system."""

        # Check if service number already exists
        self.cursor.execute(
            "SELECT id FROM personnel WHERE service_number = ?", (service_number,))
        if self.cursor.fetchone():
            return {"success": False, "error": f"Service number {service_number} already exists"}

        # Default password: NACWC123456, force password change on first login
        default_password_hash = self.hash_password("NACWC123456")

        self.cursor.execute("""
            INSERT INTO personnel (
                service_number, name, rank, rank_category, rank_order, 
                unit, platoon, email, phone, password, force_password_change, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (service_number, name, rank, rank_category, rank_order,
              unit, platoon, email, phone, default_password_hash, 1, 1))

        self.conn.commit()
        personnel_id = self.cursor.lastrowid

        # Create leave entitlement for current year
        current_year = datetime.now().year
        self.cursor.execute("""
            INSERT INTO leave_entitlement (personnel_id, year, total_days_entitled, days_used, days_remaining)
            VALUES (?, ?, 14, 0, 14)
        """, (personnel_id, current_year))

        self.conn.commit()

        return {
            "success": True,
            "personnel_id": personnel_id,
            "message": f"{name} added successfully! Default password: NACWC123456. They must change password on first login."
        }

    # =====================================================
    # LEAVE ENTITLEMENT (14-DAY LIMIT)
    # =====================================================

=======
                WHERE is_active = 1
                ORDER BY rank_category, rank_order
            """)

        return [dict(row) for row in self.cursor.fetchall()]

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
    def get_remaining_leave_days(self, personnel_id: int, year: int = None) -> int:
        """Get remaining leave days from 14-day annual entitlement"""
        if year is None:
            year = datetime.now().year

        self.cursor.execute("""
            SELECT days_remaining FROM leave_entitlement 
            WHERE personnel_id = ? AND year = ?
        """, (personnel_id, year))

        result = self.cursor.fetchone()
        if result:
            return result['days_remaining']

<<<<<<< HEAD
=======
        # No record found, create one with 14 days
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.cursor.execute("""
            INSERT INTO leave_entitlement (personnel_id, year, total_days_entitled, days_used, days_remaining)
            VALUES (?, ?, 14, 0, 14)
        """, (personnel_id, year))
        self.conn.commit()
        return 14

    def deduct_leave_days(self, personnel_id: int, days_used: int, year: int = None) -> bool:
        """Deduct used leave days from entitlement"""
        if year is None:
            year = datetime.now().year

        remaining = self.get_remaining_leave_days(personnel_id, year)
<<<<<<< HEAD
=======

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        if days_used > remaining:
            return False

        new_remaining = remaining - days_used
        days_used_total = 14 - new_remaining

        self.cursor.execute("""
            UPDATE leave_entitlement 
            SET days_used = ?, days_remaining = ?, last_updated = CURRENT_TIMESTAMP
            WHERE personnel_id = ? AND year = ?
        """, (days_used_total, new_remaining, personnel_id, year))
        self.conn.commit()
        return True

<<<<<<< HEAD
    def calculate_days(self, start_date: str, end_date: str) -> int:
        """Calculate number of days between two dates (inclusive)"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return (end - start).days + 1

=======
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
    def check_concurrent_leave(self, start_date: str, end_date: str, max_allowed: int = 10) -> Tuple[bool, str]:
        """Check if too many people are already on leave during requested period"""
        self.cursor.execute("""
            SELECT COUNT(DISTINCT personnel_id) as count
            FROM leave_requests
            WHERE status = 'approved'
            AND (
                (start_date <= ? AND end_date >= ?) OR
                (start_date <= ? AND end_date >= ?) OR
                (start_date BETWEEN ? AND ?)
            )
        """, (end_date, start_date, start_date, end_date, start_date, end_date))

        result = self.cursor.fetchone()
        current_count = result['count'] if result else 0

        if current_count >= max_allowed:
            return False, f"Too many personnel already on leave ({current_count}/{max_allowed} max)"
        return True, f"OK ({current_count}/{max_allowed} on leave)"

    def get_next_status(self, rank_category: str) -> str:
        """Determine initial status based on rank category"""
        if rank_category == 'soldier':
            return 'pending_rsm'
        return 'pending_ao'

<<<<<<< HEAD
    # =====================================================
    # LEAVE REQUEST SUBMISSION
    # =====================================================
=======
    def add_personnel(self, service_number: str, name: str, rank: str, rank_category: str,
                      rank_order: int, unit: str = None, platoon: str = None,
                      email: str = None, phone: str = None) -> Dict:
        """Add new personnel to the system"""

        # Check if service number already exists
        self.cursor.execute(
            "SELECT id FROM personnel WHERE service_number = ?", (service_number,))
        if self.cursor.fetchone():
            return {"success": False, "error": f"Service number {service_number} already exists"}

        # Insert personnel
        self.cursor.execute("""
            INSERT INTO personnel (service_number, name, rank, rank_category, rank_order, unit, platoon, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (service_number, name, rank, rank_category, rank_order, unit, platoon, email, phone))

        self.conn.commit()
        personnel_id = self.cursor.lastrowid

        # Create leave entitlement for current year
        current_year = datetime.now().year
        self.cursor.execute("""
            INSERT INTO leave_entitlement (personnel_id, year, total_days_entitled, days_used, days_remaining)
            VALUES (?, ?, 14, 0, 14)
        """, (personnel_id, current_year))

        self.conn.commit()

        return {
            "success": True,
            "personnel_id": personnel_id,
            "message": f"Personnel {name} added successfully"
        }
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018

    def submit_leave_request(self, service_number: str, start_date: str, end_date: str,
                             leave_type: str, reason: str) -> Dict:
        """Submit a new leave request"""
<<<<<<< HEAD
=======

        # Get personnel info
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        personnel = self.get_personnel_info(service_number)
        if not personnel:
            return {"success": False, "error": f"Personnel {service_number} not found"}

<<<<<<< HEAD
        total_days = self.calculate_days(start_date, end_date)
        remaining = self.get_remaining_leave_days(personnel['id'])

        if total_days > remaining:
            return {
                "success": False,
                "error": f"Insufficient leave. Requested {total_days} days, only {remaining} left"
            }

=======
        # Calculate days
        total_days = self.calculate_days(start_date, end_date)

        # Check 14-day limit
        remaining = self.get_remaining_leave_days(personnel['id'])
        if total_days > remaining:
            return {
                "success": False,
                "error": f"Insufficient leave. Requested {total_days} days, only {remaining} left (14-day annual limit)"
            }

        # Check concurrent leave
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        has_capacity, capacity_msg = self.check_concurrent_leave(
            start_date, end_date)
        if not has_capacity:
            return {"success": False, "error": capacity_msg}

<<<<<<< HEAD
        initial_status = self.get_next_status(personnel['rank_category'])

=======
        # Determine initial status
        initial_status = self.get_next_status(personnel['rank_category'])

        # Insert leave request
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.cursor.execute("""
            INSERT INTO leave_requests (
                personnel_id, leave_type, start_date, end_date, total_days, reason, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (personnel['id'], leave_type, start_date, end_date, total_days, reason, initial_status))

        self.conn.commit()
        request_id = self.cursor.lastrowid

        return {
            "success": True,
            "request_id": request_id,
<<<<<<< HEAD
=======
            "personnel": personnel,
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
            "total_days": total_days,
            "initial_status": initial_status,
            "remaining_balance": remaining - total_days,
            "message": f"Leave request #{request_id} submitted. Status: {initial_status}"
        }

<<<<<<< HEAD
    # =====================================================
    # APPROVAL WORKFLOW
    # =====================================================

    def rsm_review(self, request_id: int, rsm_service_number: str,
                   recommendation: str, comments: str = "") -> Dict:
        """RSM reviews a soldier's leave request"""
=======
    def rsm_review(self, request_id: int, rsm_service_number: str,
                   recommendation: str, comments: str = "") -> Dict:
        """RSM reviews a soldier's leave request"""

        # Verify RSM
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        rsm = self.get_personnel_info(rsm_service_number)
        if not rsm or rsm['rank'] != 'RSM':
            return {"success": False, "error": "Invalid RSM credentials"}

<<<<<<< HEAD
=======
        # Get request
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.cursor.execute("""
            SELECT lr.*, p.rank_category, p.name as personnel_name, p.rank as personnel_rank
            FROM leave_requests lr
            JOIN personnel p ON lr.personnel_id = p.id
            WHERE lr.id = ?
        """, (request_id,))
        request = self.cursor.fetchone()

        if not request:
            return {"success": False, "error": "Request not found"}

        if request['status'] != 'pending_rsm':
<<<<<<< HEAD
            return {"success": False, "error": f"Request not pending RSM review"}
=======
            return {"success": False, "error": f"Request not pending RSM review. Status: {request['status']}"}
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018

        if request['rank_category'] != 'soldier':
            return {"success": False, "error": "RSM only reviews soldier requests"}

<<<<<<< HEAD
=======
        # Update request
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.cursor.execute("""
            UPDATE leave_requests 
            SET status = 'pending_ao',
                rsm_approver_id = ?,
                rsm_approval_date = CURRENT_TIMESTAMP,
                rsm_recommendation = ?,
                rsm_comments = ?
            WHERE id = ?
        """, (rsm['id'], recommendation, comments, request_id))

        self.conn.commit()
<<<<<<< HEAD
        return {"success": True, "message": f"RSM {recommendation} the request. Forwarded to Admin Officer."}
=======

        return {
            "success": True,
            "request_id": request_id,
            "recommendation": recommendation,
            "new_status": "pending_ao",
            "message": f"RSM {recommendation} the request. Forwarded to Admin Officer."
        }
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018

    def ao_review(self, request_id: int, ao_service_number: str,
                  recommendation: str, comments: str = "") -> Dict:
        """Admin Officer reviews leave request (for everyone)"""
<<<<<<< HEAD
=======

        # Verify AO
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        ao = self.get_personnel_info(ao_service_number)
        if not ao or ao['rank'] != 'Admin Officer':
            return {"success": False, "error": "Invalid Admin Officer credentials"}

<<<<<<< HEAD
        self.cursor.execute("""
            SELECT lr.*, p.rank_category, p.name as personnel_name
=======
        # Get request
        self.cursor.execute("""
            SELECT lr.*, p.rank_category, p.name as personnel_name, p.rank as personnel_rank
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
            FROM leave_requests lr
            JOIN personnel p ON lr.personnel_id = p.id
            WHERE lr.id = ?
        """, (request_id,))
        request = self.cursor.fetchone()

        if not request:
            return {"success": False, "error": "Request not found"}

        if request['status'] != 'pending_ao':
<<<<<<< HEAD
            return {"success": False, "error": "Request not pending AO review"}

        remaining = self.get_remaining_leave_days(request['personnel_id'])
        if request['total_days'] > remaining:
            self.cursor.execute("""
                UPDATE leave_requests 
                SET status = 'rejected',
                    ao_approver_id = ?,
                    ao_approval_date = CURRENT_TIMESTAMP,
                    ao_recommendation = 'do_not_recommend',
                    ao_comments = ?
                WHERE id = ?
            """, (ao['id'], f"AUTO-REJECTED: Insufficient balance. {comments}", request_id))
            self.conn.commit()
            return {"success": False, "error": f"Request rejected. Only {remaining} days remaining."}

=======
            return {"success": False, "error": f"Request not pending AO review. Status: {request['status']}"}

        # Final check of 14-day leave balance
        remaining = self.get_remaining_leave_days(request['personnel_id'])
        if request['total_days'] > remaining:
            # Auto-reject
            self.cursor.execute("""
                UPDATE leave_requests 
                SET ao_approver_id = ?,
                    ao_approval_date = CURRENT_TIMESTAMP,
                    ao_recommendation = 'do_not_recommend',
                    ao_comments = ?,
                    status = 'rejected'
                WHERE id = ?
            """, (ao['id'], f"AUTO-REJECTED: Insufficient leave balance. {comments}", request_id))
            self.conn.commit()
            return {
                "success": False,
                "error": f"Request rejected. Only {remaining} days remaining (14-day limit)."
            }

        # Forward to Commander
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.cursor.execute("""
            UPDATE leave_requests 
            SET status = 'pending_commander',
                ao_approver_id = ?,
                ao_approval_date = CURRENT_TIMESTAMP,
                ao_recommendation = ?,
                ao_comments = ?
            WHERE id = ?
        """, (ao['id'], recommendation, comments, request_id))

        self.conn.commit()
<<<<<<< HEAD
        return {"success": True, "message": f"AO {recommendation} the request. Forwarded to Commander."}
=======

        return {
            "success": True,
            "request_id": request_id,
            "recommendation": recommendation,
            "new_status": "pending_commander",
            "message": f"AO {recommendation} the request. Forwarded to Commander."
        }
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018

    def commander_decision(self, request_id: int, commander_service_number: str,
                           decision: str, comments: str = "") -> Dict:
        """Commander makes final decision for everyone"""
<<<<<<< HEAD
        commander = self.get_personnel_info(commander_service_number)
        if not commander:
            return {"success": False, "error": "Invalid Commander credentials"}

        self.cursor.execute("""
            SELECT lr.*, p.name as personnel_name
=======

        # Verify Commander
        commander = self.get_personnel_info(commander_service_number)
        if not commander or commander['rank_category'] != 'officer':
            return {"success": False, "error": "Invalid Commander credentials"}

        # Get request
        self.cursor.execute("""
            SELECT lr.*, p.name as personnel_name, p.rank as personnel_rank
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
            FROM leave_requests lr
            JOIN personnel p ON lr.personnel_id = p.id
            WHERE lr.id = ?
        """, (request_id,))
        request = self.cursor.fetchone()

        if not request:
            return {"success": False, "error": "Request not found"}

        if request['status'] != 'pending_commander':
<<<<<<< HEAD
            return {"success": False, "error": "Request not pending Commander decision"}

=======
            return {"success": False, "error": f"Request not pending Commander decision. Status: {request['status']}"}

        # Make final decision
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        final_status = 'approved' if decision == 'approved' else 'rejected'

        self.cursor.execute("""
            UPDATE leave_requests 
            SET status = ?,
                commander_approver_id = ?,
                commander_decision_date = CURRENT_TIMESTAMP,
                commander_decision = ?,
                commander_comments = ?
            WHERE id = ?
        """, (final_status, commander['id'], decision, comments, request_id))

<<<<<<< HEAD
=======
        # If approved, deduct leave days
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        if decision == 'approved':
            self.deduct_leave_days(
                request['personnel_id'], request['total_days'])

        self.conn.commit()
<<<<<<< HEAD
        return {"success": True, "message": f"Commander has {decision} the leave request."}

    # =====================================================
    # QUERIES
    # =====================================================

    def get_pending_requests(self, role: str) -> List[Dict]:
        """Get pending requests for a specific approver"""
        if role == 'rsm':
            status_filter = 'pending_rsm'
        elif role == 'ao':
            status_filter = 'pending_ao'
        elif role == 'commander':
=======

        return {
            "success": True,
            "request_id": request_id,
            "decision": decision,
            "final_status": final_status,
            "message": f"Commander has {decision} the leave request."
        }

    def get_pending_requests(self, approver_role: str) -> List[Dict]:
        """Get pending requests for a specific approver"""

        if approver_role == 'rsm':
            status_filter = 'pending_rsm'
        elif approver_role == 'ao':
            status_filter = 'pending_ao'
        elif approver_role == 'commander':
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
            status_filter = 'pending_commander'
        else:
            return []

        self.cursor.execute("""
            SELECT 
                lr.id,
                lr.personnel_id,
                p.name as personnel_name,
                p.rank as personnel_rank,
                p.rank_category,
                p.service_number,
                lr.leave_type,
                lr.start_date,
                lr.end_date,
                lr.total_days,
                lr.reason,
                lr.submitted_date,
                lr.status
            FROM leave_requests lr
            JOIN personnel p ON lr.personnel_id = p.id
            WHERE lr.status = ?
            ORDER BY lr.submitted_date ASC
        """, (status_filter,))

        return [dict(row) for row in self.cursor.fetchall()]

    def get_my_requests(self, personnel_id: int) -> List[Dict]:
        """Get all leave requests for a specific personnel"""
<<<<<<< HEAD
=======

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.cursor.execute("""
            SELECT 
                lr.*,
                rsm.name as rsm_name,
                ao.name as ao_name,
                cdr.name as commander_name
            FROM leave_requests lr
            LEFT JOIN personnel rsm ON lr.rsm_approver_id = rsm.id
            LEFT JOIN personnel ao ON lr.ao_approver_id = ao.id
            LEFT JOIN personnel cdr ON lr.commander_approver_id = cdr.id
            WHERE lr.personnel_id = ?
            ORDER BY lr.submitted_date DESC
        """, (personnel_id,))

        return [dict(row) for row in self.cursor.fetchall()]

    def get_request_details(self, request_id: int) -> Optional[Dict]:
        """Get complete details of a leave request"""
<<<<<<< HEAD
=======

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.cursor.execute("""
            SELECT 
                lr.*,
                p.name as personnel_name,
                p.rank as personnel_rank,
                p.service_number,
                rsm.name as rsm_name,
                ao.name as ao_name,
                cdr.name as commander_name
            FROM leave_requests lr
            JOIN personnel p ON lr.personnel_id = p.id
            LEFT JOIN personnel rsm ON lr.rsm_approver_id = rsm.id
            LEFT JOIN personnel ao ON lr.ao_approver_id = ao.id
            LEFT JOIN personnel cdr ON lr.commander_approver_id = cdr.id
            WHERE lr.id = ?
        """, (request_id,))

        row = self.cursor.fetchone()
        return dict(row) if row else None

<<<<<<< HEAD
    # =====================================================
    # DUTY ROSTER
    # =====================================================

    def is_on_leave(self, personnel_id: int, date: str) -> bool:
        """Check if personnel is on approved leave on a specific date"""
=======
    def is_on_leave(self, personnel_id: int, date: str) -> bool:
        """Check if a personnel is on approved leave on a specific date"""

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.cursor.execute("""
            SELECT COUNT(*) as count
            FROM leave_requests
            WHERE personnel_id = ?
            AND status = 'approved'
            AND start_date <= ?
            AND end_date >= ?
        """, (personnel_id, date, date))

        result = self.cursor.fetchone()
        return result['count'] > 0

    def is_off_duty(self, personnel_id: int, date: str) -> bool:
<<<<<<< HEAD
        """Check if personnel has off-duty on a specific date"""
=======
        """Check if a personnel has off-duty on a specific date"""

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = date_obj.weekday()

        self.cursor.execute("""
            SELECT COUNT(*) as count
            FROM off_duty_schedule
            WHERE personnel_id = ?
            AND day_of_week = ?
            AND is_recurring = 1
            AND effective_from <= ?
            AND (effective_to IS NULL OR effective_to >= ?)
        """, (personnel_id, day_of_week, date, date))

        result = self.cursor.fetchone()
<<<<<<< HEAD
=======

        if result['count'] > 0:
            return True

        self.cursor.execute("""
            SELECT COUNT(*) as count
            FROM off_duty_exceptions
            WHERE personnel_id = ?
            AND exception_date = ?
            AND is_off_duty = 1
            AND status = 'approved'
        """, (personnel_id, date))

        result = self.cursor.fetchone()
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        return result['count'] > 0

    def get_available_personnel(self, date: str, rank_category: str = None) -> List[Dict]:
        """Get all personnel available for duty on a specific date"""
<<<<<<< HEAD
        query = """
            SELECT p.id, p.name, p.rank, p.rank_category, p.unit, p.platoon
            FROM personnel p
            WHERE p.is_active = 1 AND p.service_number != 'NACWCCORPERS'
=======

        query = """
            SELECT 
                p.id,
                p.name,
                p.rank,
                p.rank_category,
                p.unit,
                p.platoon
            FROM personnel p
            WHERE p.is_active = 1
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        """
        params = []

        if rank_category:
            query += " AND p.rank_category = ?"
            params.append(rank_category)

        self.cursor.execute(query, params)
        all_personnel = self.cursor.fetchall()

        available = []
        for person in all_personnel:
            if not self.is_on_leave(person['id'], date) and not self.is_off_duty(person['id'], date):
                available.append(dict(person))

        return available

    def get_eligible_duties(self, rank_category: str) -> List[Dict]:
        """Get duties that a personnel of given rank category can perform"""
<<<<<<< HEAD
=======

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        self.cursor.execute("""
            SELECT duty_name, default_shift
            FROM duty_types
            WHERE duty_category IN (?, 'both')
            AND is_active = 1
        """, (rank_category,))

        return [dict(row) for row in self.cursor.fetchall()]

    def generate_duty_roster(self, start_date: str, end_date: str) -> Dict:
        """Generate duty roster for a date range"""
<<<<<<< HEAD
=======

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        roster_summary = {
            "start_date": start_date,
            "end_date": end_date,
            "assignments": [],
            "statistics": {
                "total_assignments": 0,
                "soldier_assignments": 0,
                "officer_assignments": 0,
                "days_generated": 0
            }
        }

        current_date = start
        day_count = 0

        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            day_count += 1

            available_soldiers = self.get_available_personnel(
                date_str, 'soldier')
            available_officers = self.get_available_personnel(
                date_str, 'officer')

            soldier_duties = self.get_eligible_duties('soldier')
            officer_duties = self.get_eligible_duties('officer')

            soldier_idx = 0
            officer_idx = 0

<<<<<<< HEAD
            for duty in soldier_duties:
                if len(available_soldiers) == 0:
                    break
                soldier = available_soldiers[soldier_idx % len(
                    available_soldiers)]
                self.cursor.execute("""
                    INSERT INTO duty_roster (duty_date, shift, duty_type, personnel_id, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (date_str, duty['default_shift'], duty['duty_name'], soldier['id'], "Auto-assigned"))
                self.conn.commit()
=======
            # Assign soldier duties
            for duty in soldier_duties:
                if len(available_soldiers) == 0:
                    break

                soldier = available_soldiers[soldier_idx % len(
                    available_soldiers)]

                self.cursor.execute("""
                    INSERT INTO duty_roster (
                        duty_date, shift, duty_type, personnel_id, notes
                    ) VALUES (?, ?, ?, ?, ?)
                """, (date_str, duty['default_shift'], duty['duty_name'],
                      soldier['id'], "Auto-assigned from roster generation"))

                self.conn.commit()

                roster_summary["assignments"].append({
                    "date": date_str,
                    "personnel": soldier['name'],
                    "rank": soldier['rank'],
                    "duty": duty['duty_name'],
                    "shift": duty['default_shift']
                })

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
                roster_summary["statistics"]["total_assignments"] += 1
                roster_summary["statistics"]["soldier_assignments"] += 1
                soldier_idx += 1

<<<<<<< HEAD
            for duty in officer_duties:
                if len(available_officers) == 0:
                    break
                officer = available_officers[officer_idx % len(
                    available_officers)]
                self.cursor.execute("""
                    INSERT INTO duty_roster (duty_date, shift, duty_type, personnel_id, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (date_str, duty['default_shift'], duty['duty_name'], officer['id'], "Auto-assigned"))
                self.conn.commit()
=======
            # Assign officer duties
            for duty in officer_duties:
                if len(available_officers) == 0:
                    break

                officer = available_officers[officer_idx % len(
                    available_officers)]

                self.cursor.execute("""
                    INSERT INTO duty_roster (
                        duty_date, shift, duty_type, personnel_id, notes
                    ) VALUES (?, ?, ?, ?, ?)
                """, (date_str, duty['default_shift'], duty['duty_name'],
                      officer['id'], "Auto-assigned from roster generation"))

                self.conn.commit()

                roster_summary["assignments"].append({
                    "date": date_str,
                    "personnel": officer['name'],
                    "rank": officer['rank'],
                    "duty": duty['duty_name'],
                    "shift": duty['default_shift']
                })

>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
                roster_summary["statistics"]["total_assignments"] += 1
                roster_summary["statistics"]["officer_assignments"] += 1
                officer_idx += 1

            current_date += timedelta(days=1)

        roster_summary["statistics"]["days_generated"] = day_count
        return roster_summary

    def get_duty_roster(self, date: str) -> List[Dict]:
        """Get all duty assignments for a specific date"""
<<<<<<< HEAD
        self.cursor.execute("""
            SELECT dr.*, p.name as personnel_name, p.rank as personnel_rank
=======

        self.cursor.execute("""
            SELECT 
                dr.*,
                p.name as personnel_name,
                p.rank as personnel_rank
>>>>>>> aece6042afd0f3a350e00000ad8eef91899fe018
            FROM duty_roster dr
            JOIN personnel p ON dr.personnel_id = p.id
            WHERE dr.duty_date = ?
            ORDER BY dr.shift, dr.duty_type
        """, (date,))

        return [dict(row) for row in self.cursor.fetchall()]
