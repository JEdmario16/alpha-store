from flask import Blueprint, request, jsonify, make_response, Flask, current_app
from flask_login import login_user, logout_user, login_required, current_user
from alpha_store.auth.serializer import UserSchema
from alpha_store.models import User
from marshmallow import ValidationError

auth = Blueprint("auth", __name__, url_prefix="/apis/v1/auth")


def configure(app: Flask) -> None:

    app.register_blueprint(auth)
    app.logger.info("Auth configured")


@auth.route("/", methods=["GET"])
def index():

    return {
        "message": "Auth api v1",
        "status_code": 200,
    }, 200


@auth.route("/register", methods=["POST"])
def register():

    json_data = request.get_json(silent=True)

    if not json_data:
        return {
            "message": "No input data provided",
            "status_code": 400,
        }, 400

    try:
        # Load the data into the schema, validate it and create a user instance
        # The user schema post load will persist the user in the database and related tables
        user_schema = UserSchema()
        user = user_schema.load(json_data)

        current_app.logger.debug(f"User {user.username} created successfully")

        # Return the data
        return {
            "message": "User created successfully",
            "status_code": 201,
        }, 201

    except ValidationError as exc:
        # In this application, the serializer have the responsibility to validate the data, including the uniqueness of the username and email
        # So, if the data is invalid, it will raise a ValidationError
        # With that, the responsiblity of the view is just manage the response
        first_raised_error = list(exc.messages.items())[0]
        return {
            "message": f"Invalid input data: {first_raised_error[0]}: {first_raised_error[1][0]}",
            "status_code": 400,
        }, 400


@auth.route("/login", methods=["POST"])
def login():

    try:
        json_data = request.get_json(silent=True)
        usr = User.get_user_by_email(json_data["email"])

        if not usr:
            return {
                "message": "Invalid email or password",
                "status_code": 401,
            }, 401

        if usr and usr.check_password(json_data["password"]):
            login_user(usr)
            return {
                "message": "Logged in successfully",
                "status_code": 200,
            }, 200

        return {
            "message": "Invalid email or password",
            "status_code": 401,
        }, 401

    except (KeyError, TypeError) as _:
        return {
            "message": "No input data provided or missing required fields",
            "status_code": 400,
        }, 400


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return {
        "message": "Logged out successfully",
        "status_code": 200,
    }, 200
