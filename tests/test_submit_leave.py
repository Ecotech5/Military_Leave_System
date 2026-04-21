#!/usr/bin/env python3
"""
Test script for leave submission functionality
"""

from leave_management import LeaveManager
from datetime import date, timedelta
import sys


def test_leave_submission():
    print("=" * 80)
    print("TESTING LEAVE SUBMISSION FUNCTIONALITY")
    print("=" * 80)

    with LeaveManager() as lm:

        # Test 1: Soldier submitting annual leave request
        print("\n【Test 1】 Soldier Submitting Annual Leave Request")
        print("-" * 50)

        start_date = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=17)).strftime('%Y-%m-%d')

        success, message, request_id = lm.submit_leave_request(
            service_number="NG/A/001",
            start_date=start_date,
            end_date=end_date,
            leave_type="annual",
            reason="Annual leave for family vacation"
        )

        print(f"Result: {'✓ SUCCESS' if success else '✗ FAILED'}")
        print(f"Message: {message}")
        if request_id:
            print(f"Request ID: {request_id}")
            soldier_request_id = request_id

        # Test 2: Officer submitting sick leave request
        print("\n【Test 2】 Officer Submitting Sick Leave Request")
        print("-" * 50)

        start_date = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')

        success, message, request_id = lm.submit_leave_request(
            service_number="NG/O/001",
            start_date=start_date,
            end_date=end_date,
            leave_type="sick",
            reason="Medical appointment and recovery"
        )

        print(f"Result: {'✓ SUCCESS' if success else '✗ FAILED'}")
        print(f"Message: {message}")
        if request_id:
            print(f"Request ID: {request_id}")
            officer_request_id = request_id

        # Test 3: Exceeding 14-day limit
        print("\n【Test 3】 Attempting to Exceed 14-Day Limit")
        print("-" * 50)

        start_date = (date.today() + timedelta(days=20)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=40)
                    ).strftime('%Y-%m-%d')  # 21 days

        success, message, request_id = lm.submit_leave_request(
            service_number="NG/A/001",
            start_date=start_date,
            end_date=end_date,
            leave_type="annual",
            reason="Attempting to exceed limit"
        )

        print(f"Result: {'✓ SUCCESS' if success else '✗ FAILED'}")
        print(f"Message: {message}")

        # Test 4: Insufficient advance notice
        print("\n【Test 4】 Insufficient Advance Notice (Less than 7 days)")
        print("-" * 50)

        start_date = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')

        success, message, request_id = lm.submit_leave_request(
            service_number="NG/A/002",
            start_date=start_date,
            end_date=end_date,
            leave_type="annual",
            reason="Short notice leave"
        )

        print(f"Result: {'✓ SUCCESS' if success else '✗ FAILED'}")
        print(f"Message: {message}")

        # Test 5: Check leave balance
        print("\n【Test 5】 Check Leave Balance for Soldier")
        print("-" * 50)

        balance = lm.get_leave_balance_summary("NG/A/001")
        if balance:
            print(f"Personnel: NG/A/001")
            print(f"Year: {balance['year']}")
            print(f"Days Used: {balance['days_used']}")
            print(f"Days Remaining: {balance['days_remaining']}")

        # Test 6: Get request details
        if 'soldier_request_id' in locals():
            print("\n【Test 6】 Get Request Details")
            print("-" * 50)

            details = lm.get_request_details(soldier_request_id)
            if details:
                print(f"Request ID: {details['id']}")
                print(
                    f"Personnel: {details['name']} ({details['service_number']})")
                print(f"Leave Type: {details['leave_type']}")
                print(f"Duration: {details['total_days']} days")
                print(f"Status: {details['status']}")
                print(f"Submitted: {details['submitted_date']}")

        print("\n" + "=" * 80)
        print("LEAVE SUBMISSION TESTS COMPLETED")
        print("=" * 80)


def test_concurrent_leave_check():
    print("\n" + "=" * 80)
    print("TESTING CONCURRENT LEAVE CHECK")
    print("=" * 80)

    with LeaveManager() as lm:
        # Submit multiple leave requests for same period
        start_date = (date.today() + timedelta(days=15)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=20)).strftime('%Y-%m-%d')

        personnel_list = ["NG/A/002", "NG/A/003", "NG/A/004", "NG/A/005",
                          "NG/A/006", "NG/O/002", "NG/O/003"]

        # Try to exceed limit
        for i, service_number in enumerate(personnel_list[:12]):
            success, message, request_id = lm.submit_leave_request(
                service_number=service_number,
                start_date=start_date,
                end_date=end_date,
                leave_type="annual",
                reason=f"Concurrent leave test - Person {i+1}"
            )

            status = "✓" if success else "✗"
            print(f"{status} {service_number}: {message[:60]}")


if __name__ == "__main__":
    test_leave_submission()
    test_concurrent_leave_check()
