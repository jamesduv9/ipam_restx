"""
Author: James Duvall
Purpose: Database interface
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class IPAMBaseModel(DeclarativeBase):
    """
    SQLAlchemy Base object, subclass of DeclarativeBase
    """

db = SQLAlchemy(model_class=IPAMBaseModel)


def initialize_db(app):
    """
    Creates db schema based on models
    """
    with app.app_context():
        db.create_all()

def clear_db(session):
    """
    Deletes all tables in the DB
    Meant to run prior to tests
    """
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()
