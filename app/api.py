import json
import requests

# Variabile globale per generare un ID unico per ogni oggetto
next_id = 1

def Add_kv(class_name, **kwargs):
    global next_id
    
    # Impostiamo l'URL dell'API che riceverà la richiesta
    url = "http://172.18.0.1:55556/api"

    # Prepariamo la base del payload
    payload = {
        "cmd": "AddKV",
        "key": str(next_id),
    }

    # Switch per gestire i vari tipi di oggetti
    if class_name == "Donatore":
        payload["class"] = "Donatore"
        payload["value"] = json.dumps({
            "id": next_id,
            "donatore": kwargs.get("donatore"),  # Codice fiscale o altro identificatore
            "data": kwargs.get("data"),          # Data della donazione
            "gruppo": kwargs.get("gruppo"),      # Gruppo sanguigno
            "fruibile": kwargs.get("fruibile"),  # Se la sacca è fruibile
            "scadenza": kwargs.get("scadenza"),  # Scadenza della sacca
            "luogo": kwargs.get("luogo")         # Luogo della donazione
        })
    elif class_name == "Sacca":
        payload["class"] = "Sacca"
        payload["value"] = json.dumps({
            "id": next_id,
            "sacca_id": kwargs.get("sacca_id"),   # ID della sacca
            "tipo": kwargs.get("tipo"),           # Tipo della sacca (Plasma, Intera, etc.)
            "quantita": kwargs.get("quantita"),   # Quantità della sacca
            "donatore": kwargs.get("donatore"),   # Codice fiscale del donatore
            "gruppo_sanguigno": kwargs.get("gruppo_sanguigno"),  # Gruppo sanguigno
            "data_inserimento": kwargs.get("data_inserimento"),  # Data inserimento
            "test": kwargs.get("test", []),       # Lista dei test associati
            "info": kwargs.get("info", [])        # Stato della sacca (in transito, giacenza, danneggiata)
        })
    elif class_name == "Emoteca/SPOC":
        payload["class"] = "Emoteca/SPOC"
        payload["value"] = json.dumps({
            "id": next_id,
            "nome": kwargs.get("nome"),           # Nome dell'emoteca/SPOC
            "latitudine": kwargs.get("latitudine"), # Coordinate geografiche
            "longitudine": kwargs.get("longitudine"),
            "sacche": kwargs.get("sacche", [])     # Lista delle sacche associate
        })
    elif class_name == "Trasfusione":
        payload["class"] = "Trasfusione"
        payload["value"] = json.dumps({
            "id": next_id,
            "test_associati": kwargs.get("test_associati", []), # Test associati alla trasfusione
            "sacche_associate": kwargs.get("sacche_associate", []) # Sacche associate alla trasfusione
        })
    elif class_name == "Test":
        payload["class"] = "Test"
        payload["value"] = json.dumps({
            "id": next_id,
            "tipo": kwargs.get("tipo"),           # Tipo di test (preliminare, emocromo, etc.)
            "valori": kwargs.get("valori", []),   # Lista dei valori del test
            "esito": kwargs.get("esito")          # Esito del test (positivo/negativo)
        })
    elif class_name == "Transito":
        payload["class"] = "Transito"
        payload["value"] = json.dumps({
            "id": next_id,
            "da": kwargs.get("da"),              # Luogo di partenza
            "a": kwargs.get("a"),                # Luogo di arrivo
            "carico": kwargs.get("carico", [])    # Lista di sacche trasportate
        })
    elif class_name == "Moduli":
        payload["class"] = "Moduli"
        payload["value"] = json.dumps({
            "id": next_id,
            "codice_modulo": kwargs.get("codice_modulo"),  # Codice del modulo
            "opzioni": kwargs.get("opzioni", [])            # Lista delle opzioni del modulo
        })
    else:
        return {"error": "Classe non valida"}

    # A questo punto payload contiene il comando AddKV con i dati specifici
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
