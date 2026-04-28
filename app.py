#!/usr/bin/env python3
"""
Nigerian Army Leave Management System - Web Application
With Password Authentication & Force Password Change
Only Master Admin (NACWCCORPERS), Admin Officer, Chief of Staff, and Commander can add personnel
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from leave_management import LeaveManager

app = Flask(__name__)
app.secret_key = 'military_leave_system_secret_key_2024'


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with service number and password"""
    if request.method == 'POST':
        service_number = request.form['service_number']
        password = request.form['password']

        manager = LeaveManager()
        user = manager.authenticate_user(service_number, password)

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_rank'] = user['rank']
            session['user_category'] = user['rank_category']
            session['service_number'] = user['service_number']
            session['is_master_admin'] = (
                user['service_number'] == 'NACWCCORPERS')
            session['is_rsm'] = (user['rank'] == 'RSM')
            session['is_ao'] = (user['rank'] == 'Admin Officer')
            session['is_chief_of_staff'] = (user['rank'] == 'Chief of Staff')
            session['is_commander'] = (user['rank'] in [
                                       'Lieutenant Colonel', 'Colonel', 'Brigadier General', 'Major General'])

            # Check if password needs to be changed
            needs_change = manager.needs_password_change(user['id'])
            manager.close()

            if needs_change:
                flash(
                    'You must change your default password before continuing.', 'warning')
                return redirect(url_for('force_change_password'))

            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            manager.close()
            flash('Invalid service number or password', 'error')

    return render_template('login.html')


@app.route('/force_change_password', methods=['GET', 'POST'])
def force_change_password():
    """Force user to change their password on first login"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('force_change_password'))

        if len(new_password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('force_change_password'))

        if new_password == current_password:
            flash('New password must be different from current password', 'error')
            return redirect(url_for('force_change_password'))

        manager = LeaveManager()
        result = manager.change_password(
            session['user_id'], current_password, new_password)
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['error'], 'error')

    return render_template('force_change_password.html', user=session)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Allow user to change their password voluntarily"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('change_password'))

        if len(new_password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('change_password'))

        if new_password == current_password:
            flash('New password must be different from current password', 'error')
            return redirect(url_for('change_password'))

        manager = LeaveManager()
        result = manager.change_password(
            session['user_id'], current_password, new_password)
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['error'], 'error')

    return render_template('change_password.html', user=session)


@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    manager = LeaveManager()

    pending_requests = []
    if session.get('is_rsm'):
        pending_requests = manager.get_pending_requests('rsm')
    elif session.get('is_ao'):
        pending_requests = manager.get_pending_requests('ao')
    elif session.get('is_commander'):
        pending_requests = manager.get_pending_requests('commander')

    my_requests = manager.get_my_requests(session['user_id'])
    current_year = datetime.now().year
    remaining_days = manager.get_remaining_leave_days(
        session['user_id'], current_year)
    used_days = 14 - remaining_days

    # Check if user can add personnel
    can_add = manager.can_add_personnel(session['service_number'])

    manager.close()

    return render_template('dashboard.html',
                           user=session,
                           pending_requests=pending_requests,
                           my_requests=my_requests,
                           remaining_days=remaining_days,
                           used_days=used_days,
                           is_master_admin=session.get(
                               'is_master_admin', False),
                           can_add_personnel=can_add)


@app.route('/submit_leave', methods=['GET', 'POST'])
def submit_leave():
    """Submit a leave request"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    manager = LeaveManager()
    remaining_days = manager.get_remaining_leave_days(session['user_id'])
    manager.close()

    if request.method == 'POST':
        manager = LeaveManager()
        result = manager.submit_leave_request(
            service_number=session['service_number'],
            start_date=request.form['start_date'],
            end_date=request.form['end_date'],
            leave_type=request.form['leave_type'],
            reason=request.form['reason']
        )
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['error'], 'error')
        return redirect(url_for('dashboard'))

    return render_template('submit_leave.html', user=session, remaining_days=remaining_days)


@app.route('/add_personnel', methods=['GET', 'POST'])
def add_personnel():
    """Add new personnel (Admin Officer, Chief of Staff, Commander, or Master Admin only)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    manager = LeaveManager()
    can_add = manager.can_add_personnel(session['service_number'])
    manager.close()

    if not can_add:
        flash('Access denied. Only Admin Officer, Chief of Staff, Commander, or System Administrator can add personnel.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            manager = LeaveManager()

            # Get form data with proper error handling
            service_number = request.form.get('service_number', '').strip()
            name = request.form.get('name', '').strip()
            rank = request.form.get('rank', '').strip()
            rank_category = request.form.get('rank_category', '').strip()
            rank_order_str = request.form.get('rank_order', '0')
            unit = request.form.get('unit', '').strip()
            platoon = request.form.get('platoon', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()

            # Validate required fields
            if not service_number:
                flash('Service Number is required', 'error')
                return redirect(url_for('add_personnel'))
            if not name:
                flash('Name is required', 'error')
                return redirect(url_for('add_personnel'))
            if not rank:
                flash('Rank is required', 'error')
                return redirect(url_for('add_personnel'))
            if not rank_category:
                flash('Rank Category is required', 'error')
                return redirect(url_for('add_personnel'))

            # Convert rank_order to integer
            try:
                rank_order = int(rank_order_str)
            except ValueError:
                rank_order = 0

            result = manager.add_personnel(
                service_number=service_number,
                name=name,
                rank=rank,
                rank_category=rank_category,
                rank_order=rank_order,
                unit=unit if unit else None,
                platoon=platoon if platoon else None,
                email=email if email else None,
                phone=phone if phone else None
            )
            manager.close()

            if result['success']:
                flash(result['message'], 'success')
            else:
                flash(result['error'], 'error')
        except Exception as e:
            flash(f'Error adding personnel: {str(e)}', 'error')

        return redirect(url_for('dashboard'))

    return render_template('add_personnel.html', user=session)


@app.route('/view_personnel')
def view_personnel():
    """View all personnel"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    manager = LeaveManager()

    # Check if user can see all personnel
    can_view_all = manager.can_add_personnel(session['service_number'])

    if can_view_all:
        # Authorized personnel see everyone
        soldiers = manager.get_all_personnel('soldier')
        officers = manager.get_all_personnel('officer')
    else:
        # Regular users see only themselves
        user = manager.get_personnel_by_id(session['user_id'])
        if user and user['rank_category'] == 'soldier':
            soldiers = [user]
            officers = []
        elif user:
            soldiers = []
            officers = [user]
        else:
            soldiers = []
            officers = []

    manager.close()
    return render_template('view_personnel.html', soldiers=soldiers, officers=officers, user=session, can_view_all=can_view_all)


@app.route('/rsm_review/<int:request_id>', methods=['GET', 'POST'])
def rsm_review(request_id):
    """RSM review page"""
    if 'user_id' not in session or not session.get('is_rsm'):
        flash('Access denied. Only RSM can access this page.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        manager = LeaveManager()
        result = manager.rsm_review(
            request_id=request_id,
            rsm_service_number=session['service_number'],
            recommendation=request.form['recommendation'],
            comments=request.form.get('comments', '')
        )
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['error'], 'error')
        return redirect(url_for('dashboard'))

    manager = LeaveManager()
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

    if request.method == 'POST':
        manager = LeaveManager()
        result = manager.ao_review(
            request_id=request_id,
            ao_service_number=session['service_number'],
            recommendation=request.form['recommendation'],
            comments=request.form.get('comments', '')
        )
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['error'], 'error')
        return redirect(url_for('dashboard'))

    manager = LeaveManager()
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

    if request.method == 'POST':
        manager = LeaveManager()
        result = manager.commander_decision(
            request_id=request_id,
            commander_service_number=session['service_number'],
            decision=request.form['decision'],
            comments=request.form.get('comments', '')
        )
        manager.close()

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['error'], 'error')
        return redirect(url_for('dashboard'))

    manager = LeaveManager()
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
    """Generate duty roster (Commander only)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

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
        f'Roster generated! {result["statistics"]["total_assignments"]} assignments created.', 'success')
    return redirect(url_for('view_roster'))


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
