from flask import Blueprint, render_template, request, redirect, url_for,  make_response, send_file, Response
from app.models import Donatore, Ospedale
from app import db
from app.utils import hash_with_salt
from app.api import Add_kv, Get_kv, Get_key_history
from .crypto_utils import load_or_generate_key, encrypt_data, decrypt_data, generate_password
from sqlalchemy import text
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from io import BytesIO
from threading import Thread
import random
import json
import base64
import time
import redis
from urllib.parse import quote
import os

def get_next_sacca_id():
    counter_file = "sacca_id_counter.txt"

    # Se il file non esiste, crealo e parti da 1
    if not os.path.exists(counter_file):
        with open(counter_file, "w") as f:
            f.write("1")
            return 1

    # Leggi il valore attuale
    with open(counter_file, "r+") as f:
        current = int(f.read())
        new = current + 1
        f.seek(0)
        f.write(str(new))
        f.truncate()
        return new

bp = Blueprint('routes', __name__)
ALLOWED_EXTENSIONS = {'pdf'}

# Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
#Le statistiche saranno fetchate da delle funzioni in mysql
def publish_stats(app):
    with app.app_context():
        while True:
            query = db.session.execute(text("SELECT * FROM stat_osp;"))
            for result in query:
                stats = {
                    "num_sacche": result.Sacche,
                    "tot_sacche": result.SaccheTot
                }
                redis_client.set("stats:" + str(result.Id), json.dumps(stats))
            time.sleep(5)  # Publish stats every 5 seconds


# Start a background thread to simulate stats updates
def start_publish_thread(app):
    thread = Thread(target=publish_stats, args=(app,))
    thread.daemon = True
    thread.start()

# Run the background task as soon as the app starts
#TODO: Modificare la richiesta di trasferimento sacche, dovrebbe far vedere una lista da cui poter scegliere le sacche che si vogliono trasferire.
#TODO: Inserire i controlli pe i formati specifici come Codice Fiscale e Partita IVA
#TODO: Vedere se è possibile integrare le API di Open Street Maps per le coordinate (Brownie points)

@bp.route("/")

def index():

    return render_template("Landing_Page.html")


@bp.route("/submitRegistrazioneOspedale", methods=["POST"])

def registrazione_ospedale():
    # Dati form
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

    # Controllo campi obbligatori
    if not email or not password:
        esito = quote(json.dumps({"esito": "Email e password obbligatorie"}))
        response = make_response(redirect(url_for("routes.index")))
        response.set_cookie("esito", esito)
        return response

    # ID ospedale univoco
    id_casuale = random.randint(10**12, 10**18)
    while Ospedale.query.filter_by(Id=id_casuale).first():
        id_casuale = random.randint(10**12, 10**18)

    # Salvataggio nel DB
    nuovo_user = Ospedale(Usrnm=email, Pwd=password, Id=id_casuale)
    db.session.add(nuovo_user)
    db.session.commit()

    # Salvataggio su blockchain
    result = Add_kv(
        class_name="DatiOspedale",
        key=id_casuale,
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

    # Risposta e cookie
    if "error" in result:
        messaggio = {"esito": "Errore nel processo di registrazione, riprovare più tardi"}
    else:
        messaggio = {"esito": "Registrazione avvenuta con successo"}

    cookie = quote(json.dumps(messaggio))
    response = make_response(redirect(url_for("routes.index")))
    response.set_cookie("esito", cookie)
    return response


@bp.route("/inserisci_sacca", methods=["POST"])

def insertsacca():
    try:
        # Prendi i dati dal form
        id = get_next_sacca_id()
        tipo = request.form.get("tipo")
        quantita = request.form.get("quantita")
        donatore = request.form.get("donatore")
        bloodgroup = request.form.get("gruppo_sanguigno")
        insertdate = request.form.get("data_inserimento")
        tests = request.form.get("test")
        info = request.form.get("info")

        # Controllo campi obbligatori
        if not all([id, tipo, quantita, donatore, bloodgroup, insertdate, tests, info]):
            return render_template("Ospedale_dashboard.html", esito="Tutti i campi sono obbligatori.")

        # Recupera dati ospedale dal cookie
        dati_ospedale = request.cookies.get("ospedale_data")
        if not dati_ospedale:
            return render_template("Landing_Page.html", esito="Sessione scaduta, rieffettua il login.")

        key = load_or_generate_key()
        dati_ospedale = decrypt_data(dati_ospedale, key)
        id_ospedale = dati_ospedale["id"]
        luogo = dati_ospedale["nome"]

        # Aggiorna conteggi sacche
        sacche_globali = db.session.execute(text("SELECT SaccheTotali();")).scalar() or 0
        print("Sacche globali totali:", sacche_globali + 1)

        # Aggiorna sacche ospedale
        row_ospedale = db.session.execute(
            text("SELECT Sacche FROM Ospedali WHERE id = :id"),
            {"id": id_ospedale}
        ).first()

        if not row_ospedale:
            return render_template("Ospedale_dashboard.html", esito="Ospedale non trovato nel database.")

        nuove_sacche_osp = row_ospedale.Sacche + 1
        db.session.execute(
            text("UPDATE Ospedali SET Sacche = :sacche WHERE Id = :id"),
            {"sacche": nuove_sacche_osp, "id": id_ospedale}
        )
        db.session.commit()
        print("Nuovo totale sacche ospedale:", nuove_sacche_osp)

        # Se il donatore non è registrato
        query_donatore = db.session.execute(
            text("SELECT * FROM Donatori WHERE CF = HashWithSalt(:cf)"),
            {"cf": donatore}
        ).first()

        donatore_pwd = None 
        if not query_donatore:
            pwd = generate_password()
            donatore_pwd = base64.b64encode(pwd.encode("utf-8")).decode("utf-8")  # salva la password da mostrare
            db.session.execute(
                text("INSERT INTO Donatori(CF, Pwd) VALUES (:cf, :pwd)"),
                {"cf": donatore, "pwd": donatore_pwd}
            )
            db.session.commit()
            Add_kv("Donatore", key=donatore, id=donatore, pwd=pwd)

        # Aggiorna sacche del donatore
        row_donatore = db.session.execute(
            text("SELECT Sacche FROM Donatori WHERE CF = HashWithSalt(:cf)"),
            {"cf": donatore}
        ).first()

        nuove_sacche_don = row_donatore.Sacche + 1
        db.session.execute(
            text("UPDATE Donatori SET Sacche = :sacche WHERE CF = HashWithSalt(:cf)"),
            {"sacche": nuove_sacche_don, "cf": donatore}
        )
        db.session.commit()
        print("Nuovo totale sacche donatore:", nuove_sacche_don)

        # Chiave univoca comune per tutte le sacche
        chiave_sacca = random.randint(10**6, 10**9)
        print(chiave_sacca)

        # Inserisci nei tre registri
        result_globale = Add_kv(
            "Sacca",
            key=chiave_sacca,
            sacca_id=id,
            tipo=tipo,
            quantita=quantita,
            donatore=donatore,
            gruppo_sanguigno=bloodgroup,
            data_inserimento=insertdate,
            fruibile="Si",
            luogo=luogo,
            test=tests,
            info=info
        )
        print("BLOCKCHAIN RESULT:", result_globale)


        result_ospedale = Add_kv(
            "Sacca",
            key=id_ospedale,        #la chiave per saccaOspedale è id_ospedale
            sacca_id=id,
            tipo=tipo,
            quantita=quantita,
            donatore=donatore,
            gruppo_sanguigno=bloodgroup,
            data_inserimento=insertdate,
            fruibile="Si",
            luogo=luogo,
            test=tests,
            info=info
        )

        result_donatore = Add_kv(
            "Sacca",
            key=donatore,           #la chiave per la saccaDonatore è il suo codicefiscale
            sacca_id=id,
            tipo=tipo,
            quantita=quantita,
            donatore=donatore,
            gruppo_sanguigno=bloodgroup,
            data_inserimento=insertdate,
            fruibile="Si",
            luogo=luogo,
            test=tests,
            info=info
        )

        # Log errori eventuali
        if "error" in result_globale:
            print("Errore inserimento sacca globale:", result_globale)
        if "error" in result_ospedale:
            print("Errore inserimento sacca ospedale:", result_ospedale)
        if "error" in result_donatore:
            print("Errore inserimento sacca donatore:", result_donatore)


        messaggio = {
            "esito": "Sacca registrata con successo!",
            "blockchain_result": result_globale,
            "cf": donatore
        }
        print(donatore_pwd)
        if donatore_pwd:
            messaggio["pwd_donatore"] = donatore_pwd

        response = make_response(redirect(url_for("routes.dashboard_ospedale")))
        response.set_cookie("esito", quote(json.dumps(messaggio)))
        print("COOKIE DA INVIARE:", json.dumps(messaggio, indent=2))
        print("cookie", dati_ospedale)
        return response


    except Exception as e:
        print("Eccezione:", e)
        messaggio = quote(json.dumps({
            "esito": f"Errore durante l'inserimento: {str(e)}"
        }))
        response = make_response(redirect(url_for("routes.dashboard_ospedale")))
        response.set_cookie("esito", messaggio)
        return response


@bp.route("/caricaDocumentazione", methods=["POST"])

def upload_file():
    if 'document' not in request.files:
        return "No file part in request", 400

    file = request.files['document']
    esito = request.form.get("esito")
    
    if file.filename == '':
        return "No file selected", 400

    if file:
        filename = secure_filename(file.filename)
        # Read binary content
        file_content = file.read()
        # Encode in base64 for safe storage
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        # Store in blockchain
        result = Add_kv(
            class_name="Test",
            key=filename,
            content=encoded_content,
            filename=filename,
            content_type=file.content_type,
            esito=esito
        )

        if "error" in result:
            return f"Error storing document: {result['error']}", 500

        return f"Document {filename} stored successfully.", 200


@bp.route("/loginOspedale", methods=["POST"])

def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("Landing_Page.html", esito={"error": "Tutti i campi sono obbligatori"})

    try:
        # Esegui la stored procedure con SQLAlchemy
        result = db.session.execute(text(""" 
            CALL LoginOspedaleHash(:username, :password, @output_id); 
        """), {"username": username, "password": password})
        
        result = db.session.execute(text("SELECT @output_id")).first()
        ospedale_id = result[0]

        if ospedale_id == -1:
            print("sto qua, nessun ospedale")
            return render_template("Landing_Page.html", esito={"error": "Credenziali errate"})

        # Chiamata alla blockchain
        ospedale_data = Get_kv("DatiOspedale", ospedale_id)
    
        if "error" in ospedale_data:
            print("sto qua error")
            return render_template("Landing_Page.html", esito={"error": f"Errore blockchain: {ospedale_data['error']}"})
        
        key = load_or_generate_key()
        encrypted_cookie = encrypt_data(ospedale_data, key)

        response = make_response(redirect(url_for("routes.dashboard_ospedale")))
        response.set_cookie("ospedale_data", encrypted_cookie)
        return response
    except Exception as e:
        print(f"Errore durante il login: {str(e)}")
        return render_template("Landing_Page.html", esito={"error": f"Errore server: {str(e)}"})


from urllib.parse import unquote

@bp.route("/dashboardOspedale", methods=["GET"])
def dashboard_ospedale():
    dati_ospedale = request.cookies.get("ospedale_data")
    if not dati_ospedale:
        return render_template("Landing_Page.html", esito="Sessione scaduta, rieffettua il login.")

    key = load_or_generate_key()
    dati_ospedale = decrypt_data(dati_ospedale, key)
    ospedale_data = Get_kv("DatiOspedale", dati_ospedale["id"])
    
    if "error" in ospedale_data:
        return render_template("Landing_Page.html", esito={"error": f"Errore blockchain: {ospedale_data['error']}"})
    
    esito_cookie = request.cookies.get("esito")
    context = {}

    if esito_cookie:
        try:
            decoded_cookie = unquote(esito_cookie)      # <-- Aggiungi questa linea
            decoded = json.loads(decoded_cookie)        # <-- Poi fai json.loads
            context.update(decoded)
        except Exception as e:
            context["esito"] = f"Errore decodifica messaggio: {str(e)}"

    response = make_response(render_template("Ospedale_dashboard.html", **context))
    if esito_cookie:
        response.set_cookie("esito", "", expires=0)
    return response



@bp.route('/stats', methods=["GET"])

def stats():
    dati_ospedale = request.cookies.get("ospedale_data")
    if not dati_ospedale:
        return render_template("Landing_Page.html", esito="Sessione scaduta, rieffettua il login.")

    key = load_or_generate_key()
    dati_ospedale = decrypt_data(dati_ospedale, key)
    def generate():
        while True:
            stat_value = redis_client.get("stats:"+str(dati_ospedale["id"]))
            if stat_value:
                yield f"data: {stat_value.decode()}\n\n"
            else:
               yield f"data: no_change_or_default\n\n"

            
            time.sleep(1)

    return Response(generate(), content_type='text/event-stream')


@bp.route("/loginDonatore", methods=["POST"])

def donatore_login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("Login_Donatore.html", esito={"error": "Tutti i campi sono obbligatori"})

    try:
        #Controlliamo sto dannato utente
        query = db.session.execute(text("SELECT * FROM Donatori WHERE CF=HashWithSalt(:id) AND Pwd=HashWithSalt(:pwd)"),{"id": username, "pwd": password}).first()

        if not query:
            print("sto qua, nessun donatore")
            return render_template("Landing_Page.html", esito={"error": "Credenziali errate"})

        # Chiamata alla blockchain
        donatore_data = Get_kv("Donatore", username)
    
        if "error" in donatore_data:
            print("sto qua error, nessun donatore certificato")
            return render_template("Landing_Page.html", esito={"error": f"Errore blockchain: {donatore_data['error']}"})
        
        key = load_or_generate_key()
        encrypted_cookie = encrypt_data(donatore_data, key)

        response = make_response(redirect(url_for("routes.dashboard_donatore")))
        response.set_cookie("donatore_data", encrypted_cookie)
        return response
    except Exception as e:
        print(f"Errore durante il login: {str(e)}")
        return render_template("Landing_Page.html", esito={"error": f"Errore server: {str(e)}"})


@bp.route("/dashboard_donatore")
def dashboard_donatore():
    try:
        # Recupera cookie donatore
        dati_donatore = request.cookies.get("donatore_data")
        if not dati_donatore:
            return render_template("Landing_Page.html", esito="Sessione scaduta. Effettua nuovamente il login.")

        # Decripta i dati
        key = load_or_generate_key()
        dati_donatore = decrypt_data(dati_donatore, key)
        id_donatore = dati_donatore.get("id")

        # Ottieni la storia delle sacche donate
        result = Get_key_history("Sacca", id_donatore)

        if "error" in result:
            return render_template("Donatore_dashboard.html", sacche=[], errore="Errore nel recupero della cronologia.")
        
        sacche = result
        print(sacche)
        # `valori` è una lista di dizionari (una per ogni sacca)
        print("siamo qui")
        return render_template("Donatore_dashboard.html", sacche=sacche)

    except Exception as e:
        print("Eccezione nella dashboard donatore:", e)
        return render_template("Donatore_dashboard.html", sacche=[], errore="Si è verificato un errore.")

   


@bp.route("/resetDonatore", methods=["POST"])

def donatore_registrazione():
    codice_fiscale = request.form.get("codice_fiscale")

    if not codice_fiscale:
        return render_template("Ospedale_dashboard.html", esito={"error": "Tutti i campi sono obbligatori"})

    dati_esistenti = Get_kv(class_name="Donatore", key=codice_fiscale)
    if "error" in dati_esistenti:
        return render_template("Ospedale_dashboard.html")

    random_pwd = generate_password()
    print(random_pwd)
    query = db.session.execute(text("UPDATE Donatori SET CF = :cf, Pwd = :pwd WHERE CF = :oldcf AND Pwd = :oldpw"),{"cf": codice_fiscale, "pwd": random_pwd, "oldcf": dati_esistenti["id"], "oldpw": base64.b64decode(dati_esistenti["pwd"].decode("utf-8"))})
    db.session.commit()
    return render_template("Ospedale_dashboard.html", esito="Registrazione Donatore completata con successo! Sve")


@bp.route("/raggiroOspedale", methods=["GET"])

def DebugO():
    return render_template("Ospedale_dashboard.html")


@bp.route("/raggiroDonatore", methods=["GET"])

def DebugD():
    return render_template("Donatore_dashboard.html")