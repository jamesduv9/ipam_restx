from flask import Flask
from flask_restx import Api


def create_app():
    """
    Factory used to create an App, and Api object
    """
    app = Flask(__name__)

    return app

if __name__ == "__main__":
    app, api = create_app()
    app.run(debug = True)
