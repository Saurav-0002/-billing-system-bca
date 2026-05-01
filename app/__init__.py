import os, pathlib, pymysql
pymysql.install_as_MySQLdb()
from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()
mysql = MySQL()
login_manager = LoginManager()
ROOT = pathlib.Path(__file__).parent.parent

def create_app():
    app = Flask(__name__,
                template_folder=str(ROOT / 'templates'),
                static_folder=str(ROOT / 'static'))
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')
    app.config['MYSQL_HOST']        = os.getenv('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER']        = os.getenv('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD']    = os.getenv('MYSQL_PASSWORD', '')
    app.config['MYSQL_DB']          = os.getenv('MYSQL_DB', 'billing_system')
    app.config['MYSQL_PORT']        = int(os.getenv('MYSQL_PORT', 3306))
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(main_bp)
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)
    return app