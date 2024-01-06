"""
Author: James Duvall
Purpose: Database interface
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash


class IPAMBaseModel(DeclarativeBase):
    """
    SQLAlchemy Base object, subclass of DeclarativeBase
    """


db = SQLAlchemy(model_class=IPAMBaseModel)


def create_default_admin(admin_pw):
    """
    Create default admin user if it doesn't already exist
    """
    from models.user import User
    new_user = User(username="admin",
                    password_hash=generate_password_hash(
                        admin_pw),
                    permission_level=15,
                    user_active=True
                    )
    return new_user


def create_global_vrf():
    """
    Creates global vrf if it doesn't already exist
    """
    from models.vrfmodel import VRFModel
    global_vrf = VRFModel(name="Global")
    return global_vrf


def initialize_db(app, admin_pw):
    """
    Creates db schema based on models
    TODO - Should add a flag or something so admin user isn't 
    always recreated on app launch, I can see that being undesired.
    Could do a check to see if any priv 15 account exist or something
    """
    with app.app_context():
        db.create_all()
        db.session.add(create_global_vrf())
        db.session.add(create_default_admin(admin_pw))
        try:
            db.session.commit()
        except IntegrityError:
            return


def clear_db(session):
    """
    Deletes all tables in the DB
    Meant to run prior to tests
    """
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()
