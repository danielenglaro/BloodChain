from flask import Blueprint, render_template, request, redirect, url_for,  make_response, send_file, Response
from app.models import Donatore, Ospedale
from app import db
from app.utils import hash_with_salt
from app.api import Add_kv, Get_kv, Get_key_history, GetNumKeys, GetKeys, Delete_kv
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

bp = Blueprint('routes', __name__)
ALLOWED_EXTENSIONS = {'pdf'}

# Redis client
#redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
#Le statistiche saranno fetchate da delle funzioni interne che lavoreranno sulla blockchain (WIP)
#def publish_stats(app):
#    with app.app_context():
#        while True:
#            query = db.session.execute(text("SELECT * FROM stat_osp;"))
#            for result in query:
#                stats = {
#                    "num_sacche": result.Sacche,
#                    "tot_sacche": result.SaccheTot
#                }
#                redis_client.set("stats:" + str(result.Id), json.dumps(stats))
#            time.sleep(5)  # Publish stats every 5 seconds


# Start a background thread to simulate stats updates
#def start_publish_thread(app):
#    thread = Thread(target=publish_stats, args=(app,))
#    thread.daemon = True
#    thread.start()

# Run the background task as soon as the app starts
#TODO: Modificare la richiesta di trasferimento sacche, dovrebbe far vedere una lista da cui poter scegliere le sacche che si vogliono trasferire.
#TODO: Ho lasciato dei TODO in giro, dateci un'occhiata.
#TODO: Finire di rimodificare il database, che avevo fatto una porcata con il numero delle sacche. Se per domani non è fatto ci penso io quando ho accesso al pc -Luca
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

        # Aggiorna sacche ospedale
        row_ospedale = db.session.execute(
            text("SELECT * FROM Ospedali WHERE id = :id"),
            {"id": id_ospedale}
        ).first()

        if not row_ospedale:
            return render_template("Ospedale_dashboard.html", esito="Ospedale non trovato nel database.")

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

        # Chiave univoca comune per tutte le sacche
        chiave_sacca = GetNumKeys("Sacca") + 1;
        print(chiave_sacca)

        # Inserisci la sacca
        result = Add_kv(
            class_name="Sacca",
            key=str(id_ospedale) + "_" + donatore + "_" + str(chiave_sacca),
            sacca_id=chiave_sacca,
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
        print("BLOCKCHAIN RESULT:", result)

        # Log errori eventuali
        if "error" in result:
            print("Errore inserimento sacca:", result)

        messaggio = {
            "esito": "Sacca registrata con successo!",
            "blockchain_result": result,
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



#@bp.route('/stats', methods=["GET"])

#def stats():
#    dati_ospedale = request.cookies.get("ospedale_data")
#    if not dati_ospedale:
#        return render_template("Landing_Page.html", esito="Sessione scaduta, rieffettua il login.")
#
#    key = load_or_generate_key()
#    dati_ospedale = decrypt_data(dati_ospedale, key)
#    def generate():
#        while True:
#            stat_value = redis_client.get("stats:"+str(dati_ospedale["id"]))
#            if stat_value:
#                yield f"data: {stat_value.decode()}\n\n"
#            else:
#               yield f"data: no_change_or_default\n\n"
#
#           
#            time.sleep(1)
#
#    return Response(generate(), content_type='text/event-stream')


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
        #TODO: Già per come avevate modificato con il numero randomico non funzionava. Ho modificato per fare con la blockchain, vedete se funziona (visto che è più facile comunicare così che per telefono.)
        flat_keys = GetKeys("Sacca")
        
        result = [Get_key_history("Sacca", k) for k in flat_keys if id_donatore in k] #Su ogni chiave che contiene l'id donatore effettuo una Get_KV e la salvo in una lista.
        print(flat_keys)
        print(Get_key_history("Sacca", flat_keys[0]))
        print(result)
        if "error" in result:
            return render_template("Donatore_dashboard.html", sacche=[], errore="Errore nel recupero della cronologia.")
        sacche = []
        
        for i in range(len(result)): 
            sacche.append(result[i][0])
        print("-----------------\n\n\n-Qui iniziano le sacche:",sacche)
        # `valori` è una lista di dizionari (una per ogni sacca)
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


@bp.route("/inviaSacca", methods=["POST"])
def transito():
    # Dati dal form
    sacca_id = request.form.get("sacca")
    ospedale_destinazione = request.form.get("ospedale_destinazione")
    print(sacca_id, ospedale_destinazione)

    # Recupera la sacca (transazione 1)
    sacca = Get_kv("Sacca", sacca_id)
    print(sacca)
    if "error" in sacca:
        return render_template("Ospedale_dashboard.html", esitosve="❌ Errore nel recupero della sacca.")
    

    # Modifica il campo "luogo"
    sacca["luogo"] = ospedale_destinazione

    # Aggiorna la sacca (transazione 1 aggiornata)
    esito_aggiornamento = Add_kv("Sacca", sacca_id,
        sacca_id=sacca["sacca_id"],
        tipo=sacca["tipo"],
        quantita=sacca["quantita"],
        donatore=sacca["donatore"],
        gruppo_sanguigno=sacca["gruppo_sanguigno"],
        data_inserimento=sacca["data_inserimento"],
        fruibile=sacca["fruibile"],
        luogo=sacca["luogo"],
        test=sacca.get("test", []),
        info=sacca.get("info", [])
    )
    if "error" in esito_aggiornamento:
        return render_template("Ospedale_dashboard.html", esitosve="❌ Errore nell'aggiornamento della sacca.")

    # Recupera dati ospedale mittente
    dati_ospedale = request.cookies.get("ospedale_data")
    if not dati_ospedale:
        return render_template("Landing_Page.html", esitosve="Sessione scaduta, rieffettua il login.")

    key = load_or_generate_key()
    dati_ospedale = decrypt_data(dati_ospedale, key)
    id_ospedale = dati_ospedale["id"]

    # Elimina la sacca dall'ospedale mittente (transazione 2)
    delete_result = Delete_kv("DatiOspedale", sacca_id)
    if "error" in delete_result:
        return render_template("Ospedale_dashboard.html", esitosve="⚠️ Sacca modificata, ma non rimossa dalla tua emoteca.")

    # Tutto OK, rimaniamo sulla dashboard con messaggio
    return render_template("Ospedale_dashboard.html", esitosve="✅ Sacca inviata correttamente all'ospedale di destinazione.")

  
@bp.route("/visualizzaEmoteca")
def visualizza_emoteca():
    try:
        dati_ospedale = request.cookies.get("ospedale_data")
        if not dati_ospedale:
            msg = quote(json.dumps({"esito": "Sessione scaduta. Effettua nuovamente il login."}))
            response = make_response(redirect(url_for("routes.dashboard_ospedale")))
            response.set_cookie("esito", msg)
            return response

        key = load_or_generate_key()
        dati_ospedale = decrypt_data(dati_ospedale, key)
        id_ospedale = dati_ospedale.get("id")

        flat_keys = GetKeys("Sacca")
        chiavi_mie_sacche = [k for k in flat_keys if k.startswith(f"{id_ospedale}_")]
        result = [Get_key_history("Sacca", k) for k in chiavi_mie_sacche]

        if any("error" in r for r in result if isinstance(r, dict)):
            msg = quote(json.dumps({"errore": "Errore nel recupero della cronologia sacche."}))
            response = make_response(redirect(url_for("routes.dashboard_ospedale")))
            response.set_cookie("esito", msg)
            return response

        sacche = [r[0] for r in result if isinstance(r, list) and len(r) > 0]
       

        msg = quote(json.dumps({"sacche_emoteca": sacche}))
        response = make_response(redirect(url_for("routes.dashboard_ospedale")))
        response.set_cookie("esito", msg)
        return response

    except Exception as e:
        print("Errore:", e)
        msg = quote(json.dumps({"errore": "Errore imprevisto durante la visualizzazione dell’emoteca."}))
        response = make_response(redirect(url_for("routes.dashboard_ospedale")))
        response.set_cookie("esito", msg)
        return response

@bp.route("/aggiorna_stato", methods=["POST"])
def aggiorna_stato():
    print("sono qui")
    chiave_sacca = request.form.get("chiave_sacca")

    if not chiave_sacca:
        msg = quote(json.dumps({"esitosve": "Chiave sacca mancante."}))
        response = make_response(redirect(url_for("routes.dashboard_ospedale")))
        response.set_cookie("esito", msg)
        return response

    try:
        # prendi tutte le chiavi
        flat_keys = GetKeys("Sacca")
        # filtra quelle che terminano con chiave_sacca
        #TODO: fixare per fare chiave esatta
        chiavi_da_eliminare = [k for k in flat_keys if k.endswith(f"_{chiave_sacca}")]
        print(f"Chiavi da eliminare: {chiavi_da_eliminare}")

        if not chiavi_da_eliminare:
            msg = quote(json.dumps({"esitosve": f"Nessuna sacca trovata con chiave finale {chiave_sacca}."}))
        else:
            # elimina tutte le chiavi trovate
            for key in chiavi_da_eliminare:
                delete_result = Delete_kv("Sacca", key)
                print(f"Eliminazione {key}: {delete_result}")

            msg = quote(json.dumps({"esitosve": f"Sacca/e con chiave finale {chiave_sacca} eliminata/e con successo."}))

        response = make_response(redirect(url_for("routes.dashboard_ospedale")))
        response.set_cookie("esito", msg)
        return response

    except Exception as e:
        print("Errore durante l'eliminazione della sacca:", e)
        msg = quote(json.dumps({"esitosve": f"Errore imprevisto: {str(e)}"}))
        response = make_response(redirect(url_for("routes.dashboard_ospedale")))
        response.set_cookie("esito", msg)
        return response


@bp.route("/richiediSacca", methods=["POST"])
def richiedi_sacca():
    gruppo_richiesto = request.form.get("gruppo_sanguigno")
    dati_ospedale = request.cookies.get("ospedale_data")
    if not dati_ospedale:
        return render_template("Landing_Page.html", esito="Sessione scaduta, rieffettua il login.")

    key = load_or_generate_key()
    dati_ospedale = decrypt_data(dati_ospedale, key)
    id_ospedale = dati_ospedale["id"]

    if not gruppo_richiesto:
        msg = "Gruppo sanguigno mancante."
        return render_template("dashboard_ospedale.html", msg=msg, sacche_richieste=[])

    try:
        keys = GetKeys("Sacca")
        sacche_filtrate = []

        if isinstance(keys, list):
            for key in keys:
                sacca = Get_kv("Sacca", key)
                if isinstance(sacca, dict) and sacca.get("gruppo_sanguigno") == gruppo_richiesto:
                    sacche_filtrate.append(sacca)

        if not sacche_filtrate:
            msg = f"Nessuna sacca trovata per il gruppo {gruppo_richiesto}."
        else:
            msg = f"Trovate {len(sacche_filtrate)} sacche per il gruppo {gruppo_richiesto}."

        
        result = Add_kv(
            class_name="Transito", 
            key=str(id_ospedale) + "_" + str(GetNumKeys("Trasferimento")+1),
            richiedente=id_ospedale,
            filtri=[gruppo_richiesto]
        )

        return render_template(
            "Ospedale_dashboard.html",
            msg=msg,
            sacche_richieste=sacche_filtrate
        )

    except Exception as e:
        print("Errore durante la ricerca delle sacche:", e)
        msg = f"Errore imprevisto: {str(e)}"
        return render_template("Ospedale_dashboard.html", msg=msg, sacche_richieste=[])
