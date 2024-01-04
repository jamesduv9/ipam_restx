import os
from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate
from core.db import db, initialize_db
from core.authen import bp as auth


def create_app() -> Flask:
    """
    Factory used to create an App
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ipam_restx.db"
    app.config["MASTER_APIKEY"] = os.getenv("MASTER_APIKEY")
    db.init_app(app)
    migrate = Migrate(app, db)
    initialize_db(app)
    app.register_blueprint(auth)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug = True)