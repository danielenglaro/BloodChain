import json
import requests

### Questo file serve a definire le varie API che spariamo verso la blockchain ###

# Variabile globale per generare un ID unico per ogni oggetto
next_id = 1


# AddKv prende come parametro il class_name, per per instradre correttamente nello switch del payload corretto da attaccare al json. Il secondo parametro è l'insieme dei parametri
# necessari alla corretta assegnazione delle variabili

def Add_kv(class_name, **kwargs):
    global next_id
    
    # Impostiamo l'URL dell'API che riceverà la richiesta
    url = "http://localhost:55556/api"

    # Prepariamo la base del payload
    payload = {
        "cmd": "AddKV",
        "key": str(next_id),
    }

    # Switch per gestire i vari tipi di oggetti con un unico AddKv
    if class_name == "Donatore":
        payload["class"] = "Donatore"
        payload["value"] = json.dumps({
            "id": next_id,
            "donatore": kwargs.get("donatore"),                     # Codice fiscale o altro identificatore anagrafico del donatore
            "gruppo": kwargs.get("gruppo"),                         # Gruppo sanguigno (aggiungere nel caso "l'igenizzazione" per avere solamente A,B,AB,0 (+,-))
        })
    elif class_name == "Sacca":
        payload["class"] = "Sacca"
        payload["value"] = json.dumps({
            "id": next_id,
            "sacca_id": kwargs.get("sacca_id"),                     # ID della sacca prende sempre la solita variabile che gnera automaticamente all'inizio dell'api.py
            "tipo": kwargs.get("tipo"),                             # Tipo della sacca (Plasma, Intera, etc.)
            "quantita": kwargs.get("quantita"),                     # Quantità della sacca
            "donatore": kwargs.get("donatore"),                     # Codice fiscale del donatore
            "gruppo_sanguigno": kwargs.get("gruppo_sanguigno"),     # Gruppo sanguigno
            "data_inserimento": kwargs.get("data_inserimento"),     # Data inserimento
            "fruibile": kwargs.get("fruibile"),                     # Se la sacca è fruibile o come dicono le persone normali (utilizzabile)2
            "luogo": kwargs.get("luogo"),                         # Luogo della donazione 
            "test": kwargs.get("test", []),                         # Lista dei test associati
            "info": kwargs.get("info", [])                          # Stato della sacca (in transito, giacenza, danneggiata)
        })
    elif class_name == "DatiOspedale":
        payload["class"] = "DatiOspedale"
        payload["value"] = json.dumps({
            "id": next_id,
            "nome": kwargs.get("nome"),                             # Nome ufficiale dell'ospedale
            "codice_identificativo": kwargs.get("codice_identificativo"),  # Codice identificativo
            "partita_iva_cf": kwargs.get("partita_iva_cf"),         # Partita IVA o Codice Fiscale
            "indirizzo": kwargs.get("indirizzo"),                   # Indirizzo dell'ospedale
            "coordinate_gps": kwargs.get("coordinate_gps", ""),     # Coordinate GPS (opzionale)
            "regione": kwargs.get("regione"),                       # Regione
            "comune": kwargs.get("comune"),                         # Comune
            "telefono": kwargs.get("telefono"),                     # Telefono dell'ospedale
            "email_dedicata": kwargs.get("email_dedicata"),         # Email dedicata
            "sito_web": kwargs.get("sito_web", "")                   # Sito web dell'ospedale (opzionale)
        })

    elif class_name == "Emoteca/SPOC":
        payload["class"] = "Emoteca/SPOC"
        payload["value"] = json.dumps({
            "id": next_id,
            "nome": kwargs.get("nome"),                             # Nome dell'emoteca/SPOC
            "latitudine": kwargs.get("latitudine"),                 # Coordinate geografiche
            "longitudine": kwargs.get("longitudine"),               # Ancora coordinate
            "sacche": kwargs.get("sacche", [])                      # Lista delle sacche associate
        })
    elif class_name == "Trasfusione":
        payload["class"] = "Trasfusione"
        payload["value"] = json.dumps({
            "id": next_id,
            "test_associati": kwargs.get("test_associati", []),     # Test associati alla trasfusione
            "sacche_associate": kwargs.get("sacche_associate", [])  # Sacche associate alla trasfusione
        })
    elif class_name == "Test":
        payload["class"] = "Test"
        payload["value"] = json.dumps({
            "id": next_id,
            "tipo": kwargs.get("tipo"),                             # Tipo di test (preliminare, emocromo, etc.)
            "valori": kwargs.get("valori", []),                     # Lista dei valori del test
            "esito": kwargs.get("esito")                            # Esito del test (positivo/negativo)
        })
    elif class_name == "Transito":
        payload["class"] = "Transito"
        payload["value"] = json.dumps({
            "id": next_id,
            "da": kwargs.get("da"),                                 # Luogo di partenza
            "a": kwargs.get("a"),                                   # Luogo di arrivo
            "carico": kwargs.get("carico", [])                      # Lista di sacche trasportate
        })
    elif class_name == "Moduli":
        payload["class"] = "Moduli"
        payload["value"] = json.dumps({
            "id": next_id,
            "codice_modulo": kwargs.get("codice_modulo"),           # Codice del modulo
            "opzioni": kwargs.get("opzioni", [])                    # Lista delle opzioni del modulo
        })
    else:
        return {"error": "Classe non valida"}

    # A questo punto payload contiene il comando AddKV con i dati specifici e controlla solamente l'esito da restituire
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                next_id += 1
                return data
            return {"error": "Formato di risposta inatteso"}
        return {"error": f"Errore API: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
