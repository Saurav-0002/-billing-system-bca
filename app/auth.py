"""
Auth Blueprint — Login / Logout / Register
"""

import os
from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request, session)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

MAX_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 3))
LOCKOUT_MIN  = int(os.getenv('LOCKOUT_MINUTES', 15))


# ── Login ─────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        ip       = request.remote_addr

        # ── Lockout check ─────────────────────────────
        attempts = User.count_recent_attempts(username, ip, LOCKOUT_MIN)
        if attempts >= MAX_ATTEMPTS:
            flash(f'Account locked. Too many failed attempts. '
                  f'Try again after {LOCKOUT_MIN} minutes.', 'danger')
            return render_template('auth/login.html')

        # ── Fetch user ────────────────────────────────
        row = User.get_by_username(username)

        if row and check_password_hash(row['password'], password):
            if not row['is_active']:
                flash('Your account has been deactivated. Contact admin.', 'danger')
                return render_template('auth/login.html')

            user = User(row['user_id'], row['username'],
                        row['full_name'], row['role'], row['is_active'])
            login_user(user, remember=remember)
            User.update_last_login(row['user_id'])
            User.clear_attempts(username, ip)
            User.log_activity(row['user_id'], 'LOGIN', ip)

            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            User.record_failed_attempt(username, ip)
            remaining = MAX_ATTEMPTS - attempts - 1
            if remaining > 0:
                flash(f'Invalid credentials. {remaining} attempt(s) remaining.', 'danger')
            else:
                flash(f'Account locked for {LOCKOUT_MIN} minutes.', 'danger')

    return render_template('auth/login.html')


# ── Logout ────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    User.log_activity(current_user.id, 'LOGOUT', request.remote_addr)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


# ── Change Password ───────────────────────────────────────
@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    from app import mysql
    if request.method == 'POST':
        current_pw  = request.form.get('current_password', '')
        new_pw      = request.form.get('new_password', '')
        confirm_pw  = request.form.get('confirm_password', '')

        row = User.get_by_username(current_user.username)
        if not check_password_hash(row['password'], current_pw):
            flash('Current password is incorrect.', 'danger')
        elif new_pw != confirm_pw:
            flash('New passwords do not match.', 'danger')
        elif len(new_pw) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        else:
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE users SET password=%s WHERE user_id=%s",
                (generate_password_hash(new_pw), current_user.id)
            )
            mysql.connection.commit()
            cur.close()
            User.log_activity(current_user.id, 'PASSWORD_CHANGED', request.remote_addr)
            flash('Password updated successfully!', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html')
