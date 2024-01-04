"""
Author: James Duvall
Purpose: Authentication blueprint exposing user cred views
This is not apart of the overall REST api, routes are not 
meant to be RESTful
"""

from typing import Callable
from functools import wraps
from secrets import token_urlsafe
from flask import Blueprint, Response, request, current_app, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from core.db import db


bp = Blueprint(name="auth", import_name=__name__, url_prefix="/auth")


def validate_user_json(keys_: list) -> Callable:
    """
    Decorator that validates the user provides required keys for the api call 
    """
    def decorator(func: Callable):
        @wraps(func)
        def validate_user_json_dec(*args, **kwargs):
            user_data = request.get_json()
            if user_data is None:
                return jsonify({
                    "status": "Failed",
                    "errors": ["Request payload is not in JSON format"]
                }), 400

            errors = []
            for key in keys_:
                if key not in user_data:
                    errors.append(
                        f"Required key [{key}] not found in request payload")

            if errors:
                return jsonify({
                    "status": "Failed",
                    "errors": errors
                }), 400

            return func(*args, **kwargs)

        return validate_user_json_dec
    return decorator


def masterkey_required(func) -> Callable:
    """
    Decorator function used for views that require the API masterkey
    """
    @wraps(func)
    def masterkey_func_dec(**kwargs):

        if not current_app.config.get("MASTER_APIKEY"):
            return jsonify({
                "status": "Failed",
                "errors": ["App has no MASTER_APIKEY set"]
            }), 400
        if not request.headers.get("Master-Apikey"):
            return jsonify({
                "status": "Failed",
                "errors": ["No Master-Apikey header set"]
            }), 400
        if request.headers.get("Master-Apikey") != current_app.config.get("MASTER_APIKEY"):
            return jsonify({
                "status": "Failed",
                "errors": ["Invalid Master-Apikey header provided, auth failed"]
            }), 403

        return func(**kwargs)

    return masterkey_func_dec


@bp.route("/login", methods=["POST"])
@validate_user_json(keys_=["username", "password"])
def login() -> Response:
    """
    Allows the user to login with their credentials and be returned their 
    respective API token
    """
    user_data = request.get_json()
    user = db.session.query(User).filter_by(username=user_data.get("username")).first()
    if user and check_password_hash(user.password_hash, user_data.get('password')):
        return jsonify({
            "status": "Success",
            "data": {
                "apikey": user.apikey
            }
        })

    return request.get_data()


@bp.route("/register", methods=["POST"])
@masterkey_required
@validate_user_json(keys_=["username", "password"])
def register() -> Response:
    """
    View for user registration, will create a User object and store in db
    Requires that the requestor has the master key as all API users have 
    equal rights
    """
    user_data = request.get_json()
    new_user = User(username=user_data['username'],
                    password_hash=generate_password_hash(
                        user_data['password']),
                    apikey=token_urlsafe(16)
                    )
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(
            {"status": "Failed",
             "errors": ["User already exists"]}
        ), 409

    return jsonify(
        {"status": "Success"}
    )
