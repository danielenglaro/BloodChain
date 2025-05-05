from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from .utils import hash_with_salt
from .models import Ospedale
from . import db

bp = Blueprint("auth", __name__)

@bp.route("/login_ospedale", methods=["POST"])
def login_ospedale():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "error": "Username o password mancanti"}), 400

    user = Ospedale.query.filter_by(
        Usrnm=hash_with_salt(username),
        Pwd=hash_with_salt(password)
    ).first()

    if user:
        return jsonify({"success": True, "message": "Login effettuato con successo!"})
    else:
        return jsonify({"success": False, "error": "Credenziali errate"}), 401
