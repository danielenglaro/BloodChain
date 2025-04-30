from flask import Blueprint, render_template, request, redirect, url_for
from .models import User
from sqlalchemy import text
from .utils import hash_with_salt
from . import db

bp = Blueprint('auth', __name__)

@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "error": "Campi mancanti"}), 400

    query = text("""
        SELECT * FROM Donatore
        WHERE Usrnm = SHA2(CONCAT(:username, 'Luca'), 512)
        AND Pwd = SHA2(CONCAT(:password, 'Luca'), 512)
    """)
    result = db.session.execute(query, {"username": username, "password": password}).fetchone()

    if result:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Credenziali errate"}), 401
