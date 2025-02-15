from flask import Blueprint, request, jsonify
from utils.auth import register_user, login_user

auth_blueprint = Blueprint("auth_blueprint", __name__)

@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    try:
        # Expecting form data: name, imgUrl, email, password and optional system_prompt
        name = request.form.get("name", "")
        imgUrl = request.form.get("imgUrl", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        system_prompt = request.form.get("system_prompt", "")
        result = register_user(name, imgUrl, email, password, system_prompt)
        status = 200 if "message" in result else 400
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_blueprint.route("/login", methods=["POST"])
def login():
    try:
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        result = login_user(email, password)
        status = 200 if "message" in result else 400
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500
