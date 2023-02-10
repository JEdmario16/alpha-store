from flask import Blueprint, request, jsonify, make_response, Flask, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User

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
        username = json_data["username"]
        email = json_data["email"]
        password = json_data["password"]
        
    except KeyError as exc:
        return {
            "message": f"Missing key: {exc}",
            "status_code": 400,
        }, 400