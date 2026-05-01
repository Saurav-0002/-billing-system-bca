"""
User model — Flask-Login compatible
"""

from flask_login import UserMixin
from app import mysql


class User(UserMixin):
    def __init__(self, user_id, username, full_name, role, is_active):
        self.id        = user_id
        self.username  = username
        self.full_name = full_name
        self.role      = role
        self._active   = bool(is_active)

    # ── Flask-Login required ─────────────────────────────
    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self._active

    # ── Role helpers ─────────────────────────────────────
    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_manager(self):
        return self.role in ('admin', 'manager')

    # ── DB queries ───────────────────────────────────────
    @staticmethod
    def get_by_id(user_id):
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT user_id, username, full_name, role, is_active "
            "FROM users WHERE user_id = %s",
            (user_id,)
        )
        row = cur.fetchone()
        cur.close()
        if row:
            return User(row['user_id'], row['username'],
                        row['full_name'], row['role'], row['is_active'])
        return None

    @staticmethod
    def get_by_username(username):
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT user_id, username, full_name, role, is_active, password "
            "FROM users WHERE username = %s",
            (username,)
        )
        row = cur.fetchone()
        cur.close()
        return row   # returns full dict including password hash

    @staticmethod
    def update_last_login(user_id):
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE users SET last_login = NOW() WHERE user_id = %s",
            (user_id,)
        )
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def log_activity(user_id, action, ip):
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO activity_log (user_id, action, ip_address) "
            "VALUES (%s, %s, %s)",
            (user_id, action, ip)
        )
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def count_recent_attempts(username, ip, minutes=15):
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM login_attempts "
            "WHERE (username=%s OR ip_address=%s) "
            "AND attempted_at > NOW() - INTERVAL %s MINUTE",
            (username, ip, minutes)
        )
        row = cur.fetchone()
        cur.close()
        return row['cnt'] if row else 0

    @staticmethod
    def record_failed_attempt(username, ip):
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO login_attempts (username, ip_address) VALUES (%s,%s)",
            (username, ip)
        )
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def clear_attempts(username, ip):
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE FROM login_attempts WHERE username=%s OR ip_address=%s",
            (username, ip)
        )
        mysql.connection.commit()
        cur.close()
