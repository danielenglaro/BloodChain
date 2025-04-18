from flask import Flask, render_template, request
import requests
import json
import hashlib
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy # type: ignore

app = Flask(__name__)

# Configurazione del database
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+mysqlconnector://root:polpetta@172.20.0.2:3306/Users?ssl_disabled=True'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'Users'  # Nome della tabella nel database
    Usrnm = db.Column(db.String(200), primary_key=True)  # Colonna per il nome utente
    Pwd = db.Column(db.String(200), primary_key=True) 

# Funzione per aggiungere la chiave
next_id = 1  # Contatore per ID univoco

def Add_kv(class_name, data, gruppo, fruibile, scadenza, luogo, donatore):
    global next_id

    url = "http://172.18.0.1:55556/api"
    
    payload = {
        "cmd": "AddKV",
        "class": class_name,
        "key": str(next_id),  # ID univoco sequenziale
        "value": json.dumps({
            "id": next_id,
            "donatore": donatore,  # Aggiunto il campo donatore
            "data": data,
            "gruppo": gruppo,
            "fruibile": fruibile,  # Sempre "Si"
            "scadenza": scadenza,  # Ora è calcolata automaticamente
            "luogo": luogo
        })
    }
    




    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)  # Debug: stampiamo la risposta dell'API

        if response.status_code == 200:
            try:
                data = response.json()  # Proviamo a convertire in JSON
                if isinstance(data, dict):
                    next_id += 1  # Incrementiamo l'ID solo se la richiesta è andata a buon fine
                    return data
                else:
                    return {"error": "La risposta non è un dizionario come previsto"}
            except ValueError:
                return {"error": "La risposta non è un JSON valido"}
        else:
            return {"error": f"Errore API: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}  # Restituisce l'errore nel caso di eccezione

def hash_with_salt(value, salt="Luca"):
    """Applica SHA-512 con il salt fisso usato nel database."""
    return hashlib.sha512((value + salt).encode()).hexdigest()
@app.route("/")
def index():
    return render_template("Landing_Page.html")

#@app.route("/registrazione", methods=["GET"])
#def show_registration_form():
#    return render_template("registrazione.html")

#@app.route("/registrazione", methods=["POST"])
#def process_registration():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("Landing_Page.html", esito={"error": "Tutti i campi sono obbligatori"})
    
    # Calcolo hash per lo username da confrontare con quello presente nel DB
    hashed_username = hash_with_salt(username)

    # Controllo se esiste già un utente con questo username
    existing_user = User.query.filter_by(Usrnm=hashed_username).first()
    if existing_user:
        return render_template("Landing_Page.html", esito={"error": "Username già esistente"})

    try:
        nuovo_utente = User(Usrnm=username, Pwd=password)
        db.session.add(nuovo_utente)
        db.session.commit()
        esito = {"success": "Registrazione completata con successo"}
    except Exception as e:
        esito = {"error": f"Errore nel database: {str(e)}"}

    return render_template("Landing_Page.html", esito=esito)


# Route per visualizzare il form di aggiunta
@app.route("/aggiungi", methods=["GET"])
def aggiungi():
    return render_template("aggiungi.html")
7
# Route per ricevere i dati dal form e chiamare l'API (metodo POST)
@app.route("/aggiungi/invia", methods=["POST"])

@app.route("/aggiungi/invia", methods=["POST"])
def invia():
    data_str = request.form.get("data")
    gruppo = request.form.get("gruppo")
    luogo = request.form.get("luogo")
    donatore = request.form.get("donatore")

    if not data_str or not gruppo or not luogo or not donatore:
        return render_template("aggiungi.html", esito={"error": "Tutti i campi sono obbligatori"})

    # Se la data non è valida, usa quella attuale
    try:
        data_registrazione = datetime.strptime(data_str, "%Y-%m-%d")
    except ValueError:
        data_registrazione = datetime.now()

    # Converte la data in formato stringa leggibile
    data_registrazione_str = data_registrazione.strftime("%Y-%m-%d %H:%M:%S")

    # Calcola la scadenza (+42 giorni)
    data_scadenza = data_registrazione + timedelta(days=42)
    data_scadenza_str = data_scadenza.strftime("%Y-%m-%d")

    fruibile = "Si"  # Sempre "Si" di default

    # Chiamata alla funzione per aggiungere i dati alla blockchain
    esito_add = Add_kv("Sacche", data_registrazione_str, gruppo, fruibile, data_scadenza_str, luogo, donatore)
    return render_template("invio.html", esito=esito_add)


@app.route("/login", methods=["GET", "POST"])
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

@app.route("/tracciamento")
def traccia():
    return render_template("tracciamento.html")


#Funzione per renderizzare il Login per il donatore
@app.route("/loginDonatore", methods=["GET", "POST"])
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

@app.route("/loginOspedale", methods=["GET", "POST"])
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



#Funzione per renderizzare la dashboard per il donatore
@app.route("/dashDonatore")
def donatore_dashboard():
    return render_template("Donatore_dashboard.html")


#Funzione per renderizzare la dashboard per l'ospedale
@app.route("/dashOspedale")
def ospedale_dashboard():
    return render_template("Ospedale_dashboard.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)

