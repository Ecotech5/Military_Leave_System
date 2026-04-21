#!/usr/bin/env python3
"""
Test script for duty roster generation
"""

from leave_management import LeaveManager
from datetime import date, timedelta


def test_duty_roster_generation():
    print("=" * 80)
    print("TESTING DUTY ROSTER GENERATION")
    print("=" * 80)

    with LeaveManager() as lm:
        # First, approve some leave requests to test availability
        print("\n【Setup】 Approving some leave requests")
        print("-" * 50)

        # Submit and approve a leave request
        start_date = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')

        success, message, request_id = lm.submit_leave_request(
            service_number="NG/A/001",
            start_date=start_date,
            end_date=end_date,
            leave_type="annual",
            reason="Test leave for roster generation"
        )

        if success and request_id:
            lm.rsm_review(request_id, "NG/A/007", "recommend", "Test")
            lm.ao_review(request_id, "NG/O/005", "recommend", "Test")
            lm.commander_decision(request_id, "NG/O/006",
                                  "approved", "Test approval")
            print(
                f"✓ Approved leave for NG/A/001 from {start_date} to {end_date}")

        # Test availability check
        print("\n【Test 1】 Availability Check")
        print("-" * 50)

        test_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        print(f"Checking availability for {test_date}")

        available_soldiers = lm.get_available_personnel(test_date, 'soldier')
        available_officers = lm.get_available_personnel(test_date, 'officer')

        print(f"  Available Soldiers: {len(available_soldiers)}")
        print(f"  Available Officers: {len(available_officers)}")

        for soldier in available_soldiers[:5]:
            print(f"    • {soldier['name']} ({soldier['rank']})")

        # Test eligible duties
        print("\n【Test 2】 Eligible Duties by Rank Category")
        print("-" * 50)

        soldier_duties = lm.get_eligible_duties('soldier')
        officer_duties = lm.get_eligible_duties('officer')

        print(f"Soldier-eligible duties: {len(soldier_duties)}")
        for duty in soldier_duties[:5]:
            print(f"    • {duty['duty_name']} ({duty['category']})")

        print(f"\nOfficer-eligible duties: {len(officer_duties)}")
        for duty in officer_duties[:5]:
            print(f"    • {duty['duty_name']} ({duty['category']})")

        # Generate duty roster
        print("\n【Test 3】 Generate Duty Roster for Next Week")
        print("-" * 50)

        start_date = date.today().strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')

        print(f"Generating roster from {start_date} to {end_date}")

        shift_preferences = {
            'morning': {'soldiers_needed': 4, 'officers_needed': 1},
            'evening': {'soldiers_needed': 2, 'officers_needed': 1},
            'night': {'soldiers_needed': 3, 'officers_needed': 1},
            '24hr': {'soldiers_needed': 2, 'officers_needed': 1}
        }

        summary = lm.generate_duty_roster(
            start_date, end_date, shift_preferences)

        print(f"\nRoster Generation Summary:")
        print(f"  Total Assignments: {summary['total_assignments']}")
        print(f"  Assignments by Shift:")
        for shift, count in summary.get('assignments_by_shift', {}).items():
            print(f"    • {shift}: {count}")
        print(f"  Assignments by Duty:")
        for duty, count in list(summary.get('assignments_by_duty', {}).items())[:5]:
            print(f"    • {duty}: {count}")

        # Print daily roster
        print("\n【Test 4】 Display Daily Duty Roster")
        print("-" * 50)

        for i in range(3):
            roster_date = (date.today() + timedelta(days=i)
                           ).strftime('%Y-%m-%d')
            lm.print_duty_roster(roster_date)

        # Get specific date roster
        print("\n【Test 5】 Get Specific Date Roster Data")
        print("-" * 50)

        roster_date = date.today().strftime('%Y-%m-%d')
        assignments = lm.get_duty_roster(roster_date)

        print(f"Roster for {roster_date}: {len(assignments)} assignments")
        for assignment in assignments[:10]:
            print(f"  • {assignment['shift']:8} | {assignment['duty_type']:15} | "
                  f"{assignment['rank']:15} | {assignment['name']}")


def test_leave_and_off_duty_impact():
    print("\n" + "=" * 80)
    print("TESTING LEAVE AND OFF-DUTY IMPACT ON AVAILABILITY")
    print("=" * 80)

    with LeaveManager() as lm:
        # Check if personnel on leave is properly marked unavailable
        print("\n【Check】 Personnel on Leave")
        print("-" * 50)

        test_date = (date.today() + timedelta(days=8)).strftime('%Y-%m-%d')

        # Check specific personnel
        personnel = lm.get_personnel_info("NG/A/001")
        if personnel:
            is_on_leave = lm.is_on_leave(personnel['id'], test_date)
            is_off_duty = lm.is_off_duty(personnel['id'], test_date)
            is_available = not (is_on_leave or is_off_duty)

            print(
                f"Personnel: {personnel['name']} ({personnel['service_number']})")
            print(f"  Date: {test_date}")
            print(f"  On Leave: {is_on_leave}")
            print(f"  Off Duty: {is_off_duty}")
            print(f"  Available for Duty: {is_available}")

        # Check off-duty schedule
        print("\n【Check】 Off-Duty Schedule (Weekends)")
        print("-" * 50)

        weekend_date = (date.today() + timedelta(days=(5 -
                        date.today().weekday()) % 7)).strftime('%Y-%m-%d')

        personnel_list = ["NG/A/002", "NG/O/001"]
        for service_number in personnel_list:
            personnel = lm.get_personnel_info(service_number)
            if personnel:
                is_off_duty = lm.is_off_duty(personnel['id'], weekend_date)
                print(
                    f"{personnel['name']}: Off-duty on {weekend_date}? {is_off_duty}")


if __name__ == "__main__":
    test_duty_roster_generation()
    test_leave_and_off_duty_impact()
