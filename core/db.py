from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class IPAMBaseModel(DeclarativeBase):
    """
    SQLAlchemy Base object, subclass of DeclarativeBase
    """

db = SQLAlchemy(model_class=IPAMBaseModel)

def initialize_db(app):
    """
    
    """
    with app.app_context():
        db.create_all()