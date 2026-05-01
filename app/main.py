"""
Main Blueprint — Root redirect + error handlers
"""

from flask import Blueprint, redirect, url_for, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500
