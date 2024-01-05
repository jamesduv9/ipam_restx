import os
from flask import Flask
from flask_migrate import Migrate
from core.db import db, initialize_db
from core.authen import bp as auth
from routes import api


def create_app(environment="prod") -> Flask:
    """
    Factory used to create an App
    """
    app = Flask(__name__)
    if environment == "test":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ipam_restx_test.db"
        app.config["MASTER_APIKEY"] = "test_key"
    if environment == "prod":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ipam_restx.db"
        app.config["MASTER_APIKEY"] = os.getenv("MASTER_APIKEY")
    db.init_app(app)
    Migrate(app, db)
    initialize_db(app)
    app.register_blueprint(auth)
    api.init_app(app)
    
    return app

if __name__ == "__main__":
    app = create_app(environment="prod")
    app.run(debug = True)
