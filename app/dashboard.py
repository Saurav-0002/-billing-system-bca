"""
Dashboard Blueprint — Main landing after login
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import mysql

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def get_dashboard_stats():
    """Fetch stats for dashboard widgets. Safe defaults if tables don't exist yet."""
    cur = mysql.connection.cursor()
    stats = {
        'today_sales':     0,
        'today_revenue':   0.0,
        'total_users':     0,
        'low_stock_count': 0,
        'pending_returns': 0,
        'monthly_revenue': [],
        'payment_split':   {},
        'top_products':    [],
        'recent_sales':    [],
    }

    # Total users
    try:
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE is_active=1")
        stats['total_users'] = cur.fetchone()['cnt']
    except Exception:
        pass

    # Today's sales count & revenue (safe — sales table may not exist yet)
    try:
        cur.execute("""
            SELECT COUNT(*) AS cnt, COALESCE(SUM(grand_total),0) AS rev
            FROM sales WHERE DATE(sale_date)=CURDATE()
        """)
        row = cur.fetchone()
        stats['today_sales']   = row['cnt']
        stats['today_revenue'] = float(row['rev'])
    except Exception:
        pass

    # Low stock count
    try:
        cur.execute("""
            SELECT COUNT(*) AS cnt FROM products
            WHERE stock_qty <= reorder_level AND is_active=1
        """)
        stats['low_stock_count'] = cur.fetchone()['cnt']
    except Exception:
        pass

    # Pending returns
    try:
        cur.execute("""
            SELECT COUNT(*) AS cnt FROM returns WHERE status='pending'
        """)
        stats['pending_returns'] = cur.fetchone()['cnt']
    except Exception:
        pass

    # Monthly revenue (last 6 months)
    try:
        cur.execute("""
            SELECT DATE_FORMAT(sale_date,'%b %Y') AS month,
                   COALESCE(SUM(grand_total),0) AS total
            FROM sales
            WHERE sale_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY YEAR(sale_date), MONTH(sale_date)
            ORDER BY sale_date ASC
        """)
        stats['monthly_revenue'] = cur.fetchall()
    except Exception:
        pass

    # Payment split
    try:
        cur.execute("""
            SELECT payment_mode, COUNT(*) AS cnt
            FROM sales WHERE DATE(sale_date)=CURDATE()
            GROUP BY payment_mode
        """)
        for row in cur.fetchall():
            stats['payment_split'][row['payment_mode']] = row['cnt']
    except Exception:
        pass

    # Top 5 products today
    try:
        cur.execute("""
            SELECT p.name, SUM(si.qty) AS sold
            FROM sale_items si
            JOIN products p ON p.product_id=si.product_id
            JOIN sales s ON s.sale_id=si.sale_id
            WHERE DATE(s.sale_date)=CURDATE()
            GROUP BY si.product_id
            ORDER BY sold DESC LIMIT 5
        """)
        stats['top_products'] = cur.fetchall()
    except Exception:
        pass

    # Recent 5 sales
    try:
        cur.execute("""
            SELECT s.invoice_number, s.grand_total,
                   s.payment_mode, s.sale_date,
                   COALESCE(c.name,'Walk-in') AS customer
            FROM sales s
            LEFT JOIN customers c ON c.customer_id=s.customer_id
            ORDER BY s.sale_date DESC LIMIT 5
        """)
        stats['recent_sales'] = cur.fetchall()
    except Exception:
        pass

    cur.close()
    return stats


@dashboard_bp.route('/')
@dashboard_bp.route('/index')
@login_required
def index():
    stats = get_dashboard_stats()
    return render_template('dashboard/index.html', stats=stats)
