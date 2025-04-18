from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from .api import Add_kv

bp = Blueprint('routes', __name__)

@bp.route("/")
def index():
    return render_template("Landing_Page.html")

@bp.route("/aggiungi", methods=["GET"])
def aggiungi():
    return render_template("aggiungi.html")

@bp.route("/aggiungi/invia", methods=["POST"])
def invia():
    data_str = request.form.get("data")
    gruppo = request.form.get("gruppo")
    luogo = request.form.get("luogo")
    donatore = request.form.get("donatore")

    if not data_str or not gruppo or not luogo or not donatore:
        return render_template("aggiungi.html", esito={"error": "Tutti i campi sono obbligatori"})

    try:
        data_registrazione = datetime.strptime(data_str, "%Y-%m-%d")
    except ValueError:
        data_registrazione = datetime.now()

    data_str = data_registrazione.strftime("%Y-%m-%d %H:%M:%S")
    scadenza_str = (data_registrazione + timedelta(days=42)).strftime("%Y-%m-%d")
    esito = Add_kv("Sacche", data_str, gruppo, "Si", scadenza_str, luogo, donatore)
    return render_template("invio.html", esito=esito)

@bp.route("/tracciamento")
def traccia():
    return render_template("tracciamento.html")
