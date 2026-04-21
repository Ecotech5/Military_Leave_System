#!/usr/bin/env python3
"""
Nigerian Army Leave Management System - Web Application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from leave_management import LeaveManager

app = Flask(__name__)
app.secret_key = 'military_leave_system_secret_key_2024'


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""

    if request.method == 'POST':
        service_number = request.form['service_number']

        manager = LeaveManager()
        personnel = manager.get_personnel_info(service_number)
        manager.close()

        if personnel:
            session['user_id'] = personnel['id']
            session['user_name'] = personnel['name']
            session['user_rank'] = personnel['rank']
            session['user_category'] = personnel['rank_category']
            session['service_number'] = service_number
            session['is_rsm'] = (personnel['rank'] == 'RSM')
            session['is_ao'] = (personnel['rank'] == 'Admin Officer')
            session['is_commander'] = (personnel['rank'] in [
                                       'Lieutenant Colonel', 'Colonel', 'Brigadier General', 'Major General'])

            flash(f'Welcome, {personnel["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid service number. Please try again.', 'error')

    return render_template('login.html')


@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Main dashboard"""

    if 'user_id' not in session:
        return redirect(url_for('login'))

    manager = LeaveManager()

    # Get pending requests based on role
    pending_requests = []
    if session.get('is_rsm'):
        pending_requests = manager.get_pending_requests('rsm')
    elif session.get('is_ao'):
        pending_requests = manager.get_pending_requests('ao')
    elif session.get('is_commander'):
        pending_requests = manager.get_pending_requests('commander')

    # Get user's leave requests
    my_requests = manager.get_my_requests(session['user_id'])

    # Get leave balance
    current_year = datetime.now().year
    remaining_days = manager.get_remaining_leave_days(
        session['user_id'], current_year)
    used_days = 14 - remaining_days

    manager.close()

    return render_template('dashboard.html',
                           user=session,
                           pending_requests=pending_requests,
                           my_requests=my_requests,
                           remaining_days=remaining_days,
                           used_days=used_days)


@app.route('/add_personnel', methods=['GET', 'POST'])
def add_personnel():
    """Add new personnel (Admin only)"""

    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Only Admin Officer or Commander can add personnel
    if not (session.get('is_ao') or session.get('is_commander')):
        flash('Only Admin Officer or Commander can add personnel', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        service_number = request.form['service_number']
        name = request.form['name']
        rank = request.form['rank']
        rank_category = request.form['rank_category']
        rank_order = int(request.form['rank_order'])
        unit = request.form.get('unit', '')
        platoon = request.form.get('platoon', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')

        manager = LeaveManager()
        result = manager.add_personnel(
            service_number=service_number,
            name=name,
            rank=rank,
            rank_category=rank_category,
            rank_order=rank_order,
            unit=unit,
            platoon=platoon,
            email=email,
            phone=phone
        )
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['error'], 'error')

    return render_template('add_personnel.html', user=session)


@app.route('/submit_leave', methods=['GET', 'POST'])
def submit_leave():
    """Submit a leave request"""

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        reason = request.form['reason']

        manager = LeaveManager()
        result = manager.submit_leave_request(
            service_number=session['service_number'],
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            reason=reason
        )
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['error'], 'error')

        return redirect(url_for('dashboard'))

    return render_template('submit_leave.html', user=session)


@app.route('/rsm_review/<int:request_id>', methods=['GET', 'POST'])
def rsm_review(request_id):
    """RSM review page"""

    if 'user_id' not in session or not session.get('is_rsm'):
        flash('Access denied. Only RSM can access this page.', 'error')
        return redirect(url_for('dashboard'))

    manager = LeaveManager()

    if request.method == 'POST':
        recommendation = request.form['recommendation']
        comments = request.form.get('comments', '')

        result = manager.rsm_review(
            request_id=request_id,
            rsm_service_number=session['service_number'],
            recommendation=recommendation,
            comments=comments
        )
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['error'], 'error')

        return redirect(url_for('dashboard'))

    # GET request - show the review form
    request_data = manager.get_request_details(request_id)
    manager.close()

    if not request_data:
        flash('Request not found', 'error')
        return redirect(url_for('dashboard'))

    return render_template('rsm_review.html', request=request_data, user=session)


@app.route('/ao_review/<int:request_id>', methods=['GET', 'POST'])
def ao_review(request_id):
    """Admin Officer review page"""

    if 'user_id' not in session or not session.get('is_ao'):
        flash('Access denied. Only Admin Officer can access this page.', 'error')
        return redirect(url_for('dashboard'))

    manager = LeaveManager()

    if request.method == 'POST':
        recommendation = request.form['recommendation']
        comments = request.form.get('comments', '')

        result = manager.ao_review(
            request_id=request_id,
            ao_service_number=session['service_number'],
            recommendation=recommendation,
            comments=comments
        )
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['error'], 'error')

        return redirect(url_for('dashboard'))

    # GET request - show the review form
    request_data = manager.get_request_details(request_id)
    manager.close()

    if not request_data:
        flash('Request not found', 'error')
        return redirect(url_for('dashboard'))

    return render_template('ao_review.html', request=request_data, user=session)


@app.route('/commander_decision/<int:request_id>', methods=['GET', 'POST'])
def commander_decision(request_id):
    """Commander decision page"""

    if 'user_id' not in session or not session.get('is_commander'):
        flash('Access denied. Only Commander can access this page.', 'error')
        return redirect(url_for('dashboard'))

    manager = LeaveManager()

    if request.method == 'POST':
        decision = request.form['decision']
        comments = request.form.get('comments', '')

        result = manager.commander_decision(
            request_id=request_id,
            commander_service_number=session['service_number'],
            decision=decision,
            comments=comments
        )
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['error'], 'error')

        return redirect(url_for('dashboard'))

    # GET request - show the decision form
    request_data = manager.get_request_details(request_id)
    manager.close()

    if not request_data:
        flash('Request not found', 'error')
        return redirect(url_for('dashboard'))

    return render_template('commander_decision.html', request=request_data, user=session)


@app.route('/view_roster')
def view_roster():
    """View duty roster"""

    if 'user_id' not in session:
        return redirect(url_for('login'))

    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

    manager = LeaveManager()
    roster = manager.get_duty_roster(date_str)
    manager.close()

    return render_template('roster.html', roster=roster, selected_date=date_str, user=session)


@app.route('/generate_roster', methods=['POST'])
def generate_roster():
    """Generate duty roster"""

    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Only Commander can generate roster
    if not session.get('is_commander'):
        flash('Only Commander can generate duty roster', 'error')
        return redirect(url_for('dashboard'))

    start_date = request.form.get(
        'start_date', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.form.get(
        'end_date', (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))

    manager = LeaveManager()
    result = manager.generate_duty_roster(start_date, end_date)
    manager.close()

    flash(
        f'Roster generated! {result["statistics"]["total_assignments"]} assignments created for {result["statistics"]["days_generated"]} days.', 'success')
    return redirect(url_for('view_roster'))


@app.route('/view_personnel')
def view_personnel():
    """View all personnel"""

    if 'user_id' not in session:
        return redirect(url_for('login'))

    manager = LeaveManager()
    soldiers = manager.get_all_personnel('soldier')
    officers = manager.get_all_personnel('officer')
    manager.close()

    return render_template('view_personnel.html', soldiers=soldiers, officers=officers, user=session)


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
