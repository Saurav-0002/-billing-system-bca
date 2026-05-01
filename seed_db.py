"""
seed_db.py — Run ONCE after schema.sql to create default users.
Usage: python seed_db.py
"""

import pymysql
pymysql.install_as_MySQLdb()

import os
from dotenv import load_dotenv
import MySQLdb
from werkzeug.security import generate_password_hash

load_dotenv()

def seed():
    conn = MySQLdb.connect(
        host   = os.getenv('MYSQL_HOST', 'localhost'),
        user   = os.getenv('MYSQL_USER', 'root'),
        passwd = os.getenv('MYSQL_PASSWORD', ''),
        db     = os.getenv('MYSQL_DB', 'billing_system'),
        port   = int(os.getenv('MYSQL_PORT', 3306)),
    )
    cur = conn.cursor()

    users = [
        ('Administrator', 'admin',   'admin@123',   'admin'),
        ('Manager One',   'manager', 'manager@123', 'manager'),
        ('Cashier One',   'cashier', 'cashier@123', 'cashier'),
    ]

    for full_name, username, password, role in users:
        pw_hash = generate_password_hash(password)
        cur.execute("""
            INSERT INTO users (full_name, username, password, role)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE password = VALUES(password)
        """, (full_name, username, pw_hash, role))
        print(f"  + User '{username}' ({role}) created.")

    conn.commit()
    cur.close()
    conn.close()

    print("\nDatabase seeded!")
    print("-" * 38)
    print("  admin   / admin@123")
    print("  manager / manager@123")
    print("  cashier / cashier@123")
    print("-" * 38)
    print("Change passwords after first login!\n")

if __name__ == '__main__':
    seed()
