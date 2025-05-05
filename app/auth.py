from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import text
from .utils import hash_with_salt
from . import db
import mysql.connector

bp = Blueprint('auth', __name__)

@bp.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("Landing_Page.html", esito={"error": "Tutti i campi sono obbligatori"})

        # Query SQL grezza che esegue l'hash nel DB
        query = text("""
            SELECT * FROM Donatore
            WHERE Usrnm = SHA2(CONCAT(:username, 'Luca'), 512)
            AND Pwd = SHA2(CONCAT(:password, 'Luca'), 512)
        """)

        result = db.session.execute(query, {"username": username, "password": password}).fetchone()

        if result:
            return render_template("Landing_Page.html", esito={"success": "Login effettuato con successo!"})
        else:
            msg='Credenziali incorrette svejate'
    return render_template('/pre_Donatore',msg = msg)


@bp.route("/login_ospedale", methods=["POST"])
def login_ospedale():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Verifica se username e password sono forniti
    if not username or not password:
        return jsonify({"success": False, "error": "Username o password mancanti"}), 400

    # Query per verificare le credenziali dell'ospedale (puoi personalizzare la query)
    query = text("""
        SELECT * FROM Ospedale
        WHERE username = :username
        AND password = SHA2(CONCAT(:password, 'Luca'), 512)
    """)

    try:
        result = db.session.execute(query, {"username": username, "password": password}).fetchone()
        if result:
            return jsonify({"success": True, "message": "Login effettuato con successo!"})
        else:
            return jsonify({"success": False, "error": "Credenziali errate"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": "Errore nel server"}), 500

@bp.route("/submitRegistrazioneOspedale", methods=["POST"])
def registra_ospedale():
    from flask import request, redirect, url_for, flash
    from sqlalchemy import text
    db = current_app.db

    # Ottieni i dati dal form
    nome = request.form.get("nome_ospedale")
    codice = request.form.get("codice_identificativo")
    partita_iva = request.form.get("partita_iva")
    indirizzo = request.form.get("indirizzo")
    coordinate = request.form.get("gps")
    regione = request.form.get("regione")
    comune = request.form.get("comune")
    telefono = request.form.get("telefono")
    sito_web = request.form.get("sito_web")

    # Query per inserimento
    insert_query = text("""
        INSERT INTO Dati_Ospedali (
            Nome, Codice, PartitaIVA, Indirizzo, Coordinate, Regione, Comune, Telefono, SitoWeb
        ) VALUES (
            :nome, :codice, :partita_iva, :indirizzo, :coordinate, :regione, :comune, :telefono, :sito_web
        )
    """)

    try:
        db.session.execute(insert_query, {
            "nome": nome,
            "codice": codice,
            "partita_iva": partita_iva,
            "indirizzo": indirizzo,
            "coordinate": coordinate,
            "regione": regione,
            "comune": comune,
            "telefono": telefono,
            "sito_web": sito_web
        })
        db.session.commit()
        flash("Ospedale registrato con successo.", "success")
        return redirect(url_for("main.index"))
    except Exception as e:
        db.session.rollback()
        flash("Errore nella registrazione: " + str(e), "danger")
        return redirect(url_for("main.index"))
