from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mysql+mysqlconnector://root:polpetta@db-mysql:3306/Users?ssl_disabled=True'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "chiave_super_segretissima"

    db.init_app(app)

    from .routes import bp as routes_bp
    from .auth import bp as auth_bp
    app.register_blueprint(routes_bp)
    app.register_blueprint(auth_bp)

    return app
