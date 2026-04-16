import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://"
        f"{os.environ.get('MYSQLUSER', 'root')}:"
        f"{os.environ.get('MYSQLPASSWORD', '')}@"
        f"{os.environ.get('MYSQLHOST', 'localhost')}:"
        f"{int(os.environ.get('MYSQLPORT', 3306))}/"
        f"{os.environ.get('MYSQLDATABASE', 'railway')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
