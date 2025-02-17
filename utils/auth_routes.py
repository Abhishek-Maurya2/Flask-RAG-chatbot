from flask import Blueprint, request, jsonify
from utils.auth import register_user, login_user

auth_blueprint = Blueprint("auth_blueprint", __name__)

@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    try:
        # Retrieve signup information from the form data
        name = request.form.get("name", "")
        imgUrl = request.form.get("imgUrl", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        system_prompt = request.form.get("system_prompt", "")

        # Register the user and capture the result and status code
        result, status_code = register_user(name, imgUrl, email, password, system_prompt)

        return jsonify(result), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_blueprint.route("/login", methods=["POST"])
def login():
    try:
        # Retrieve login credentials from JSON data in the POST body
        data = request.get_json()
        email = data.get("email", "")
        password = data.get("password", "")
        
        # Attempt to login the user and capture the result and status code
        result, status_code = login_user(email, password)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500