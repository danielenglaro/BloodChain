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


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("Landing_Page.html", esito={"error": "Tutti i campi sono obbligatori"})

        # Hash delle credenziali inserite
        hashed_username = hash_with_salt(username)
        hashed_password = hash_with_salt(password)

        # Verifica nel database
        user = User.query.filter_by(Usrnm=hashed_username, Pwd=hashed_password).first()

        if user:
            return render_template("Landing_Page.html", esito={"success": "Login effettuato con successo!"})
        else:
            return render_template("Landing_Page.html", esito={"error": "Credenziali errate"})

    return render_template("Landing_Page.html")

@bp.route("/tracciamento")
def traccia():
    return render_template("tracciamento.html")


#Funzione per renderizzare il Login per il donatore
@bp.route("/loginDonatore", methods=["GET", "POST"])
def donataore_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("Login_Donatore.html", esito={"error": "Tutti i campi sono obbligatori"})

        # Calcolo hash per lo username da confrontare con quello presente nel DB
        hashed_username = hash_with_salt(username)

        # Controllo se esiste già un utente con questo username
        existing_user = User.query.filter_by(Usrnm=hashed_username).first()
        if existing_user:
            return render_template("Login_Donatore.html", esito={"error": "Username già esistente"})

        try:
            nuovo_utente = User(Usrnm=username, Pwd=password)
            db.session.add(nuovo_utente)
            db.session.commit()
            esito = {"success": "Registrazione completata con successo"}
        except Exception as e:
            esito = {"error": f"Errore nel database: {str(e)}"}

        return render_template("Login_Donatore.html", esito=esito)

    return render_template("Donatore_dashboard.html")


#Funzione per renderizzare il Login per l'ospedale
from flask import redirect, url_for

@bp.route("/loginOspedale", methods=["GET", "POST"])
def ospedale_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("Login_Ospedale.html", esito={"error": "Tutti i campi sono obbligatori"})

        # Calcolo hash dello username per la ricerca nel DB
        hashed_username = hash_with_salt(username)

        # Controllo se esiste l'utente con quello username
        existing_user = User.query.filter_by(Usrnm=hashed_username).first()

        if not existing_user or existing_user.Pwd != password:
            return render_template("Login_Ospedale.html", esito={"error": "Credenziali non valide"})

        # Login riuscito → reindirizza alla dashboard
        return redirect(url_for("dashOspedale"))

    return render_template("Login_Ospedale.html")

