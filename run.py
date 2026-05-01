"""
run.py — Entry point for development server
Usage: python run.py
"""

# ── Windows fix: use PyMySQL as MySQLdb drop-in ──────────
import pymysql
pymysql.install_as_MySQLdb()

from app import create_app
from datetime import datetime

app = create_app()

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
