#!/usr/bin/env python3
"""
Test script for complete approval workflow
"""

from leave_management import LeaveManager
from datetime import date, timedelta
import time


def test_soldier_approval_workflow():
    print("=" * 80)
    print("TESTING SOLDIER APPROVAL WORKFLOW (RSM → AO → Commander)")
    print("=" * 80)

    with LeaveManager() as lm:
        # Step 1: Soldier submits leave request
        print("\n【Step 1】 Soldier Submits Leave Request")
        print("-" * 50)

        start_date = (date.today() + timedelta(days=14)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=21)).strftime('%Y-%m-%d')

        success, message, request_id = lm.submit_leave_request(
            service_number="NG/A/001",
            start_date=start_date,
            end_date=end_date,
            leave_type="annual",
            reason="Family wedding attendance"
        )

        print(f"Result: {'✓' if success else '✗'} {message}")
        if not success:
            return

        print(f"Request ID: {request_id}")

        # Check status
        details = lm.get_request_details(request_id)
        print(f"Initial Status: {details['status']}")

        # Step 2: RSM Review
        print("\n【Step 2】 RSM Review")
        print("-" * 50)

        success, message = lm.rsm_review(
            request_id=request_id,
            rsm_service_number="NG/A/007",  # RSM
            recommendation="recommend",
            comments="Verified. Soldier has good record. Recommend approval."
        )

        print(f"Result: {'✓' if success else '✗'} {message}")

        details = lm.get_request_details(request_id)
        print(f"Status after RSM: {details['status']}")
        if details.get('rsm_recommendation'):
            print(f"RSM Recommendation: {details['rsm_recommendation']}")
            print(f"RSM Comments: {details['rsm_comments']}")

        # Step 3: Admin Officer Review
        print("\n【Step 3】 Admin Officer Review")
        print("-" * 50)

        success, message = lm.ao_review(
            request_id=request_id,
            ao_service_number="NG/O/005",  # Admin Officer
            recommendation="recommend",
            comments="Leave balance sufficient. Administrative requirements met."
        )

        print(f"Result: {'✓' if success else '✗'} {message}")

        details = lm.get_request_details(request_id)
        print(f"Status after AO: {details['status']}")
        if details.get('ao_recommendation'):
            print(f"AO Recommendation: {details['ao_recommendation']}")
            print(f"AO Comments: {details['ao_comments']}")

        # Step 4: Commander Final Decision
        print("\n【Step 4】 Commander Final Decision")
        print("-" * 50)

        success, message = lm.commander_decision(
            request_id=request_id,
            commander_service_number="NG/O/006",  # Commander
            decision="approved",
            comments="Approved. Ensure smooth handover before proceeding on leave."
        )

        print(f"Result: {'✓' if success else '✗'} {message}")

        # Final Status
        details = lm.get_request_details(request_id)
        print(f"\nFinal Status: {details['status']}")
        print(f"Commander Decision: {details['commander_decision']}")
        print(f"Commander Comments: {details['commander_comments']}")

        # Check leave balance after approval
        balance = lm.get_leave_balance_summary("NG/A/001")
        if balance:
            print(f"\nUpdated Leave Balance:")
            print(f"  Days Used: {balance['days_used']}")
            print(f"  Days Remaining: {balance['days_remaining']}")


def test_officer_approval_workflow():
    print("\n" + "=" * 80)
    print("TESTING OFFICER APPROVAL WORKFLOW (AO → Commander only)")
    print("=" * 80)

    with LeaveManager() as lm:
        # Step 1: Officer submits leave request
        print("\n【Step 1】 Officer Submits Leave Request")
        print("-" * 50)

        start_date = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=15)).strftime('%Y-%m-%d')

        success, message, request_id = lm.submit_leave_request(
            service_number="NG/O/002",
            start_date=start_date,
            end_date=end_date,
            leave_type="annual",
            reason="Professional development course"
        )

        print(f"Result: {'✓' if success else '✗'} {message}")
        if not success:
            return

        print(f"Request ID: {request_id}")

        # Check status (should be pending_ao directly - no RSM)
        details = lm.get_request_details(request_id)
        print(
            f"Initial Status: {details['status']} (No RSM required for officers)")

        # Step 2: Admin Officer Review
        print("\n【Step 2】 Admin Officer Review")
        print("-" * 50)

        success, message = lm.ao_review(
            request_id=request_id,
            ao_service_number="NG/O/005",  # Admin Officer
            recommendation="recommend",
            comments="Officer in good standing. Leave balance sufficient."
        )

        print(f"Result: {'✓' if success else '✗'} {message}")

        details = lm.get_request_details(request_id)
        print(f"Status after AO: {details['status']}")

        # Step 3: Commander Final Decision
        print("\n【Step 3】 Commander Final Decision")
        print("-" * 50)

        success, message = lm.commander_decision(
            request_id=request_id,
            commander_service_number="NG/O/006",  # Commander
            decision="approved",
            comments="Approved for professional development."
        )

        print(f"Result: {'✓' if success else '✗'} {message}")

        # Final Status
        details = lm.get_request_details(request_id)
        print(f"\nFinal Status: {details['status']}")


def test_rejection_workflow():
    print("\n" + "=" * 80)
    print("TESTING REJECTION WORKFLOW")
    print("=" * 80)

    with LeaveManager() as lm:
        # Submit request
        print("\n【Step 1】 Submit Request")
        print("-" * 50)

        start_date = (date.today() + timedelta(days=12)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=18)).strftime('%Y-%m-%d')

        success, message, request_id = lm.submit_leave_request(
            service_number="NG/A/003",
            start_date=start_date,
            end_date=end_date,
            leave_type="annual",
            reason="Personal vacation"
        )

        print(f"Result: {'✓' if success else '✗'} {message}")

        # RSM Review
        print("\n【Step 2】 RSM Review")
        print("-" * 50)

        success, message = lm.rsm_review(
            request_id=request_id,
            rsm_service_number="NG/A/007",
            recommendation="do_not_recommend",
            comments="Critical operational period. Cannot spare personnel."
        )

        print(f"Result: {'✓' if success else '✗'} {message}")

        # AO Review (will forward anyway)
        print("\n【Step 3】 AO Review")
        print("-" * 50)

        success, message = lm.ao_review(
            request_id=request_id,
            ao_service_number="NG/O/005",
            recommendation="do_not_recommend",
            comments="RSM does not recommend due to operational requirements."
        )

        print(f"Result: {'✓' if success else '✗'} {message}")

        # Commander Rejection
        print("\n【Step 4】 Commander Decision - REJECTION")
        print("-" * 50)

        success, message = lm.commander_decision(
            request_id=request_id,
            commander_service_number="NG/O/006",
            decision="rejected",
            comments="Request denied due to operational commitments."
        )

        print(f"Result: {'✓' if success else '✗'} {message}")

        details = lm.get_request_details(request_id)
        print(f"\nFinal Status: {details['status']}")
        print(f"Commander Decision: {details['commander_decision']}")
        print(f"Commander Comments: {details['commander_comments']}")


def test_pending_requests_view():
    print("\n" + "=" * 80)
    print("VIEWING PENDING REQUESTS BY APPROVER ROLE")
    print("=" * 80)

    with LeaveManager() as lm:
        # Submit a few requests
        start_date = (date.today() + timedelta(days=20)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=25)).strftime('%Y-%m-%d')

        for service_number in ["NG/A/004", "NG/A/005", "NG/O/003"]:
            lm.submit_leave_request(
                service_number=service_number,
                start_date=start_date,
                end_date=end_date,
                leave_type="annual",
                reason="Test pending requests"
            )

        # Get pending for RSM
        print("\n【Pending for RSM】")
        print("-" * 50)
        pending = lm.get_pending_requests('rsm')
        for req in pending:
            print(f"  ID: {req['id']} | {req['name']} ({req['service_number']}) | "
                  f"Type: {req['leave_type']} | Days: {req['total_days']}")

        # Get pending for AO
        print("\n【Pending for Admin Officer】")
        print("-" * 50)
        pending = lm.get_pending_requests('ao')
        for req in pending:
            print(f"  ID: {req['id']} | {req['name']} ({req['service_number']}) | "
                  f"Type: {req['leave_type']} | Days: {req['total_days']}")


if __name__ == "__main__":
    test_soldier_approval_workflow()
    test_officer_approval_workflow()
    test_rejection_workflow()
    test_pending_requests_view()
