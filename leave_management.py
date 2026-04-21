#!/usr/bin/env python3
"""
Nigerian Army Leave Management System - Core Business Logic
Handles all leave requests, approvals, and duty roster generation
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List

DB_PATH = 'database/military_leave_system.db'


class LeaveManager:
    """Main class for managing leave requests and duty rosters"""

    def __init__(self, db_path: str = DB_PATH):
        """Initialize database connection"""
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

    def calculate_days(self, start_date: str, end_date: str) -> int:
        """Calculate number of days between two dates (inclusive)"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return (end - start).days + 1

    def get_personnel_info(self, service_number: str) -> Optional[Dict]:
        """Get personnel information by service number"""
        self.cursor.execute("""
            SELECT id, name, rank, rank_category, email, phone, unit
            FROM personnel 
            WHERE service_number = ? AND is_active = 1
        """, (service_number,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_personnel_by_id(self, personnel_id: int) -> Optional[Dict]:
        """Get personnel information by ID"""
        self.cursor.execute("""
            SELECT id, name, rank, rank_category, service_number, email, phone
            FROM personnel 
            WHERE id = ? AND is_active = 1
        """, (personnel_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_personnel(self, category: str = None) -> List[Dict]:
        """Get all personnel, optionally filtered by category"""
        if category:
            self.cursor.execute("""
                SELECT id, service_number, name, rank, rank_category, unit, phone, email
                FROM personnel 
                WHERE rank_category = ? AND is_active = 1
                ORDER BY rank_order
            """, (category,))
        else:
            self.cursor.execute("""
                SELECT id, service_number, name, rank, rank_category, unit, phone, email
                FROM personnel 
                WHERE is_active = 1
                ORDER BY rank_category, rank_order
            """)

        return [dict(row) for row in self.cursor.fetchall()]

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

        # No record found, create one with 14 days
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

    def submit_leave_request(self, service_number: str, start_date: str, end_date: str,
                             leave_type: str, reason: str) -> Dict:
        """Submit a new leave request"""

        # Get personnel info
        personnel = self.get_personnel_info(service_number)
        if not personnel:
            return {"success": False, "error": f"Personnel {service_number} not found"}

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
        has_capacity, capacity_msg = self.check_concurrent_leave(
            start_date, end_date)
        if not has_capacity:
            return {"success": False, "error": capacity_msg}

        # Determine initial status
        initial_status = self.get_next_status(personnel['rank_category'])

        # Insert leave request
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
            "personnel": personnel,
            "total_days": total_days,
            "initial_status": initial_status,
            "remaining_balance": remaining - total_days,
            "message": f"Leave request #{request_id} submitted. Status: {initial_status}"
        }

    def rsm_review(self, request_id: int, rsm_service_number: str,
                   recommendation: str, comments: str = "") -> Dict:
        """RSM reviews a soldier's leave request"""

        # Verify RSM
        rsm = self.get_personnel_info(rsm_service_number)
        if not rsm or rsm['rank'] != 'RSM':
            return {"success": False, "error": "Invalid RSM credentials"}

        # Get request
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
            return {"success": False, "error": f"Request not pending RSM review. Status: {request['status']}"}

        if request['rank_category'] != 'soldier':
            return {"success": False, "error": "RSM only reviews soldier requests"}

        # Update request
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

        return {
            "success": True,
            "request_id": request_id,
            "recommendation": recommendation,
            "new_status": "pending_ao",
            "message": f"RSM {recommendation} the request. Forwarded to Admin Officer."
        }

    def ao_review(self, request_id: int, ao_service_number: str,
                  recommendation: str, comments: str = "") -> Dict:
        """Admin Officer reviews leave request (for everyone)"""

        # Verify AO
        ao = self.get_personnel_info(ao_service_number)
        if not ao or ao['rank'] != 'Admin Officer':
            return {"success": False, "error": "Invalid Admin Officer credentials"}

        # Get request
        self.cursor.execute("""
            SELECT lr.*, p.rank_category, p.name as personnel_name, p.rank as personnel_rank
            FROM leave_requests lr
            JOIN personnel p ON lr.personnel_id = p.id
            WHERE lr.id = ?
        """, (request_id,))
        request = self.cursor.fetchone()

        if not request:
            return {"success": False, "error": "Request not found"}

        if request['status'] != 'pending_ao':
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

        return {
            "success": True,
            "request_id": request_id,
            "recommendation": recommendation,
            "new_status": "pending_commander",
            "message": f"AO {recommendation} the request. Forwarded to Commander."
        }

    def commander_decision(self, request_id: int, commander_service_number: str,
                           decision: str, comments: str = "") -> Dict:
        """Commander makes final decision for everyone"""

        # Verify Commander
        commander = self.get_personnel_info(commander_service_number)
        if not commander or commander['rank_category'] != 'officer':
            return {"success": False, "error": "Invalid Commander credentials"}

        # Get request
        self.cursor.execute("""
            SELECT lr.*, p.name as personnel_name, p.rank as personnel_rank
            FROM leave_requests lr
            JOIN personnel p ON lr.personnel_id = p.id
            WHERE lr.id = ?
        """, (request_id,))
        request = self.cursor.fetchone()

        if not request:
            return {"success": False, "error": "Request not found"}

        if request['status'] != 'pending_commander':
            return {"success": False, "error": f"Request not pending Commander decision. Status: {request['status']}"}

        # Make final decision
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

        # If approved, deduct leave days
        if decision == 'approved':
            self.deduct_leave_days(
                request['personnel_id'], request['total_days'])

        self.conn.commit()

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

    def is_on_leave(self, personnel_id: int, date: str) -> bool:
        """Check if a personnel is on approved leave on a specific date"""

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
        """Check if a personnel has off-duty on a specific date"""

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
        return result['count'] > 0

    def get_available_personnel(self, date: str, rank_category: str = None) -> List[Dict]:
        """Get all personnel available for duty on a specific date"""

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

        self.cursor.execute("""
            SELECT duty_name, default_shift
            FROM duty_types
            WHERE duty_category IN (?, 'both')
            AND is_active = 1
        """, (rank_category,))

        return [dict(row) for row in self.cursor.fetchall()]

    def generate_duty_roster(self, start_date: str, end_date: str) -> Dict:
        """Generate duty roster for a date range"""

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

                roster_summary["statistics"]["total_assignments"] += 1
                roster_summary["statistics"]["soldier_assignments"] += 1
                soldier_idx += 1

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

                roster_summary["statistics"]["total_assignments"] += 1
                roster_summary["statistics"]["officer_assignments"] += 1
                officer_idx += 1

            current_date += timedelta(days=1)

        roster_summary["statistics"]["days_generated"] = day_count
        return roster_summary

    def get_duty_roster(self, date: str) -> List[Dict]:
        """Get all duty assignments for a specific date"""

        self.cursor.execute("""
            SELECT 
                dr.*,
                p.name as personnel_name,
                p.rank as personnel_rank
            FROM duty_roster dr
            JOIN personnel p ON dr.personnel_id = p.id
            WHERE dr.duty_date = ?
            ORDER BY dr.shift, dr.duty_type
        """, (date,))

        return [dict(row) for row in self.cursor.fetchall()]
