import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://"
        f"{os.environ.get('MYSQLUSER') or os.environ.get('DB_USER', 'root')}:"
        f"{os.environ.get('MYSQLPASSWORD') or os.environ.get('DB_PASSWORD', '')}@"
        f"{os.environ.get('MYSQLHOST') or os.environ.get('DB_HOST', 'localhost')}:"
        f"{os.environ.get('MYSQLPORT') or os.environ.get('DB_PORT', '3306')}/"
        f"{os.environ.get('MYSQLDATABASE') or os.environ.get('DB_NAME', 'fitness_app')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
