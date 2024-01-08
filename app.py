"""
Author: James Duvall
Purpose: Basic IPAM REST API using Flask, 
meant for learning purposes while pursuing Cisco DevNet Expert
"""

import os
from flask import Flask
from flask_migrate import Migrate
from core.db import db, initialize_db
from core.authen import bp as auth
from routes import api
from waitress import serve

def create_app(environment: str = "prod") -> Flask:
    """
    Factory used to create an App
    """
    app = Flask(__name__)
    if environment == "test":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["MASTER_APIKEY"] = "test_key"
        app.config["DEBUG"] = True

    if environment == "prod":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ipam_restx.db"
        app.config["MASTER_APIKEY"] = os.getenv("MASTER_APIKEY")

    db.init_app(app)
    Migrate(app, db)
    initialize_db(app, admin_pw=app.config["MASTER_APIKEY"])
    app.register_blueprint(auth)
    api.init_app(app)

    @app.route("/health_check")
    def health_check():
        return "Healthy!"

    return app


if __name__ == "__main__":
    app = create_app(environment="prod")
    serve(app, host="0.0.0.0", port=8443, url_scheme="https")
