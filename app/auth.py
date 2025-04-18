from flask import Blueprint, render_template, request, redirect, url_for
from .models import User
from .utils import hash_with_salt
from . import db

bp = Blueprint('auth', __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("Landing_Page.html", esito={"error": "Tutti i campi sono obbligatori"})

        hashed_username = hash_with_salt(username)
        hashed_password = hash_with_salt(password)

        user = User.query.filter_by(Usrnm=hashed_username, Pwd=hashed_password).first()

        if user:
            return render_template("Landing_Page.html", esito={"success": "Login effettuato con successo!"})
        else:
            return render_template("Landing_Page.html", esito={"error": "Credenziali errate"})

    return render_template("Landing_Page.html")

@bp.route("/loginOspedale", methods=["GET", "POST"])
def ospedale_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hashed_username = hash_with_salt(username)

        existing_user = User.query.filter_by(Usrnm=hashed_username).first()

        if not existing_user or existing_user.Pwd != password:
            return render_template("Login_Ospedale.html", esito={"error": "Credenziali non valide"})

        return redirect(url_for("routes.ospedale_dashboard"))

    return render_template("Login_Ospedale.html")

@bp.route("/dashOspedale")
def ospedale_dashboard():
    return render_template("Ospedale_dashboard.html")
