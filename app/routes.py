from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Donatore, Ospedale
from app import db
from app.utils import hash_with_salt
from app.api import Add_kv

bp = Blueprint('routes', __name__)

@bp.route("/")
def index():
    return render_template("Landing_Page.html")

@bp.route("/autenticazioneOspedale")
def authOspedale():
    return render_template("pre_Ospedale.html")

@bp.route("/submitRegistrazioneOspedale", methods=["POST"])
def registrazione_ospedale():
    # Form
    nome = request.form.get("nome")
    codice_identificativo = request.form.get("codice_identificativo")
    partita_iva_cf = request.form.get("partita_iva_cf")
    indirizzo = request.form.get("indirizzo")
    coordinate_gps = request.form.get("coordinate_gps")
    regione = request.form.get("regione")
    comune = request.form.get("comune")
    telefono = request.form.get("telefono")
    email_dedicata = request.form.get("email_dedicata")
    sito_web = request.form.get("sito_web")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return render_template("Landing_Page.html", esito={"error": "Email e password obbligatorie"})

    

    nuovo_user = Ospedale(Usrnm=email, Pwd=password)
    db.session.add(nuovo_user)
    db.session.commit()

    result = Add_kv(
        class_name="DatiOspedale",
        nome=nome,
        codice_identificativo=codice_identificativo,
        partita_iva_cf=partita_iva_cf,
        indirizzo=indirizzo,
        coordinate_gps=coordinate_gps,
        regione=regione,
        comune=comune,
        telefono=telefono,
        email_dedicata=email_dedicata,
        sito_web=sito_web
    )
    print("RISULTATO BLOCKCHAIN:", result) 

    if "error" in result:
        return render_template("Landing_Page.html", esito={"error": f"Errore blockchain: {result['error']}"})

    return render_template("Ospedale_dashboard.html", esito={"success": "Registrazione avvenuta con successo!"})

@bp.route("/loginOspedale", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("Landing_Page.html", esito={"error": "Tutti i campi sono obbligatori"})

    user = Ospedale.query.filter_by(
        Usrnm=hash_with_salt(username),
        Pwd=hash_with_salt(password)
    ).first()

    if user:
        return render_template("Ospedale_dashboard.html", esito={"success": "Login effettuato con successo!"})
    else:
        return render_template("Landing_Page.html", esito={"error": "Credenziali errate"})

@bp.route("/loginDonatore", methods=["POST"])
def donatore_login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("Login_Donatore.html", esito={"error": "Tutti i campi sono obbligatori"})

    if Donatore.query.filter_by(Usrnm=hash_with_salt(username)).first():
        return render_template("Login_Donatore.html", esito={"error": "Username già registrato"})

    nuovo = User(Usrnm=hash_with_salt(username), Pwd=hash_with_salt(password))
    db.session.add(nuovo)
    db.session.commit()
    return render_template("Login_Donatore.html", esito={"success": "Registrazione completata con successo"})



@bp.route("/dashboardOspedale")
def dashboard_ospedale():
    return render_template("Ospedale_dashboard.html")

@bp.route("/dashboardDonatore")
def dashboard_donatore():
    return render_template("Donatore_dashboard.html")
