from flask import Flask

from app.extensions import db, jwt, migrate
from app.config import Config

#IMPORTACION DE LAS RUTAS
from app.users.routes import users_bp
from app.auth.routes import auth_bp
from app.locations.routes import locations_bp

#MAPEO DE LOS MODELOS DE LA BASE DE DATOS
from app.users.model import User
from app.locations.model import BurialSpace, Sector

def create_app():
  
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(locations_bp)

    return app