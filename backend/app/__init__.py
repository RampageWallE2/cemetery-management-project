from flask import Flask

from app.extensions import db, jwt, migrate
from app.users.routes import users_bp
from app.auth.routes import auth_bp
from app.users.model import User

def create_app():
  
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)

    return app