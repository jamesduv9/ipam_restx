"""
Author: James Duvall
Purpose: Authentication blueprint exposing user cred views
    This is not apart of the overall REST api, routes are not 
    meant to be RESTful
Caveat: This was created for learning purposes, authentication is rolled 
    out manually, and likely has security bugs, not meant for production use
"""
from datetime import datetime, timedelta, timezone
from typing import Callable
from functools import wraps
from secrets import token_urlsafe
from flask import Blueprint, Response, request, current_app, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
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


def apikey_validate(permission_level: int) -> Callable:
    """
    Decorator that validates the user has a valid apikey, and the
    user has sufficent permissions to use the API.
    Will be used by all api calls, each requiring specific permission levels
    """
    def decorator(func):
        @wraps(func)
        def validate_apikey(*args, **kwargs):
            if not request.headers.get("X-Ipam-Apikey"):
                return {
                    "status": "Failed",
                    "errors": ["No X-Ipam-Apikey header set"]
                }, 400
            target_user = db.session.query(User).filter_by(
                apikey=request.headers.get("X-Ipam-Apikey")).first()
            if not target_user:
                return {
                    "status": "Failed",
                    "errors": ["No user found with provided X-Ipam-Apikey, auth failed"]
                }, 401

            if target_user.apikey_expiration <= datetime.now():
                return {
                    "status": "Failed",
                    "errors":
                        [f"apikey is expired as of {target_user.apikey_expiration}. Please relogin at /auth/login"]
                }, 400

            if target_user.permission_level < permission_level:
                return {
                    "status": "Failed",
                    "errors": ["User does not have sufficient permission"]
                }, 403
            return func(*args, **kwargs)

        return validate_apikey

    return decorator


def masterkey_required(func: Callable) -> Callable:
    """
    Decorator function used for views that require the API masterkey
    """
    @wraps(func)
    def masterkey_func_dec(*args, **kwargs):

        if not current_app.config.get("MASTER_APIKEY"):
            return jsonify({
                "status": "Failed",
                "errors": ["App has no MASTER_APIKEY set"]
            }), 400
        if not request.headers.get("X-Ipam-Apikey"):
            return jsonify({
                "status": "Failed",
                "errors": ["No X-Ipam-Apikey header set"]
            }), 400
        if request.headers.get("X-Ipam-Apikey") != current_app.config.get("MASTER_APIKEY"):
            return jsonify({
                "status": "Failed",
                "errors": ["Invalid X-Ipam-Apikey header provided, auth failed"]
            }), 403

        return func(*args, **kwargs)

    return masterkey_func_dec

@bp.route("/login", methods=["POST"])
@validate_user_json(keys_=["username", "password"])
def login() -> Response:
    """
    Allows the user to login with their credentials and be returned their 
    respective API token
    """
    user_data = request.get_json()
    user = db.session.query(User).filter_by(
        username=user_data.get("username")).first()
    if user and check_password_hash(user.password_hash, user_data.get('password')):
        user.apikey = token_urlsafe(16)
        user.apikey_expiration = datetime.now(
            tz=timezone.utc) + timedelta(days=1)
        db.session.add(user)
        db.session.commit()
        return jsonify({
            "status": "Success",
            "data": {
                "X-Ipam-Apikey": user.apikey,
                "expiration": user.apikey_expiration,
                "permission_level": user.permission_level
            }
        }), 200
    
    return jsonify({
        "status": "Failed",
        "errors": ["password not correct or invalid user provided"]
    })


@bp.route("/register", methods=["POST"])
@validate_user_json(keys_=["username", "password", "permission_level"])
@masterkey_required
def register() -> Response:
    """
    View for user registration, will create a User object and store in db
    Requires that the requestor has the master key 
    """
    user_data = request.get_json()
    new_user = User(username=user_data['username'],
                    password_hash=generate_password_hash(
                        user_data['password']),
                    permission_level=user_data['permission_level']
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


@bp.route("/delete", methods=["POST"])
@validate_user_json(keys_=["username"])
@masterkey_required
def delete() -> Response:
    """
    View for user deletion, will query the user based off unique username
    deletes the user and commits to DB
    requires master key
    """
    user_data = request.get_json()
    user = db.session.query(User).filter_by(
        username=user_data.get("username")).first()
    if not user:
        return jsonify({
            "status": "Failed",
            "errors": ["User deletion failed, user does not exist"]
        })
    try:
        db.session.delete(user)
        db.session.commit()
    except UnmappedInstanceError:
        return jsonify({
            "status": "Failed",
            "errors": ["User deletion failed, user does not exist"]
        })
    return jsonify({
        "status": "Success"
    })
