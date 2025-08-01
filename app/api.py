import json
import requests

### Questo file serve a definire le varie API che spariamo verso la blockchain ###

# Variabile globale per generare un ID unico per ogni oggetto
next_id = 1


# AddKv prende come parametro il class_name, per per instradre correttamente nello switch del payload corretto da attaccare al json. Il secondo parametro è l'insieme dei parametri
# necessari alla corretta assegnazione delle variabili

def Add_kv(class_name, key, **kwargs):
    global next_id
    
    # Impostiamo l'URL dell'API che riceverà la richiesta
    url = "http://localhost:55556/api"

    # Prepariamo la base del payload
    payload = {
        "cmd": "AddKV",
        "key": str(key),
    }

    # Switch per gestire i vari tipi di oggetti con un unico AddKv
    if class_name == "Donatore":
        payload["class"] = "Donatore"
        payload["value"] = json.dumps({
            "id": key,
            "pwd": kwargs.get("pwd")
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
            "luogo": kwargs.get("luogo"),                          # Luogo della donazione 
            "test": kwargs.get("test", []),                         # Lista dei test associati
            "info": kwargs.get("info", [])                          # Stato della sacca (in transito, giacenza, danneggiata)
        })

    elif class_name == "DatiOspedale":
        payload["class"] = "DatiOspedale"
        payload["value"] = json.dumps({
            "id": key,
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

    elif class_name == "Transito":
        payload["class"] = "Transito"
        payload["value"] = json.dumps({
            "id": next_id,
            "richiedente": kwargs.get("richiedente"),
            "filtri": kwargs.get("filtri", [])
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


def Get_kv(class_name, key):
    url = "http://localhost:55556/api"  # o l'IP corretto, se cambi

    payload = {
        "cmd": "GetKV",
        "class": class_name,
        "key": str(key)
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "answer" in data:
                # Decodifica il campo JSON 'value' annidato come stringa
                value_json = data["answer"].get("value", "{}")
                value = json.loads(value_json)
                return value  # restituisce un dizionario con i dati effettivi
            return {"error": "Risposta senza campo 'answer' valido"}
        return {"error": f"Errore API: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def GetNumKeys(class_name):
    url = "http://localhost:55556/api"

    payload = {
        "cmd": "GetNumKeys",
        "class": class_name,
        "key":""
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "answer" in data:
                # Decodifica il campo JSON 'value' annidato come stringa
                value = data["answer"].get("numkeys")
                return value  # restituisce un dizionario con i dati effettivi
            return {"error": "Risposta senza campo 'answer' valido"}
        return {"error": f"Errore API: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
    

def GetKeys(class_name):
    url = "http://localhost:55556/api"

    payload = {
        "cmd": "GetKeys",
        "class": class_name,
        "key":""
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "answer" in data:
                # Decodifica il campo JSON 'value' annidato come stringa
                raw_keys = data["answer"].get("keys", [])
                keys = [item[0] for item in raw_keys if item]
                return keys  # restituisce un dizionario con i dati effettivi
            return {"error": "Risposta senza campo 'answer' valido"}
        return {"error": f"Errore API: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def Get_key_history(class_name, key):
    url = "http://localhost:55556/api"

    payload = {
        "cmd": "GetKeyHistory",
        "class": class_name,
        "key": str(key)
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "answer" in data:
                history = []
                for entry in data["answer"]:
                    record = {
                        "isDelete": entry.get("isDelete"),
                        "timestamp": entry.get("timestamp"),
                        "txId": entry.get("txId"),
                        "data": {}
                    }

                    data_raw = entry.get("data", "")
                    if data_raw.strip() != "":
                        try:
                            parsed = json.loads(data_raw)
                            if "value" in parsed:
                                # parsed["value"] è ancora stringa JSON?
                                value_raw = parsed["value"]
                                if isinstance(value_raw, str) and value_raw.strip() != "":
                                    try:
                                        record["data"] = json.loads(value_raw)
                                    except json.JSONDecodeError as e:
                                        print(f"Errore decoding nested value: {e}")
                                        record["data"] = {}
                                else:
                                    record["data"] = value_raw
                            else:
                                record["data"] = parsed
                        except json.JSONDecodeError as e:
                            print(f"Errore decoding data: {e}")
                            record["data"] = {}
                    else:
                        record["data"] = {}

                    history.append(record)
                return history
            return {"error": "Risposta senza campo 'answer' valido"}
        return {"error": f"Errore API: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}



def Delete_kv(class_name, key):
    url = "http://localhost:55556/api"  # Aggiorna l'host se necessario

    payload = {
        "cmd": "DelKV",
        "class": class_name,
        "key": str(key)
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return {"success": True, "message": f"Elemento {key} della classe {class_name} eliminato con successo."}
            return {"error": "Eliminazione fallita o chiave non trovata"}
        return {"error": f"Errore API: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
