import requests
import json

next_id = 1

def Add_kv(class_name, data, gruppo, fruibile, scadenza, luogo, donatore):
    global next_id
    url = "http://172.18.0.1:55556/api"
    payload = {
        "cmd": "AddKV",
        "class": class_name,
        "key": str(next_id),
        "value": json.dumps({
            "id": next_id,
            "donatore": donatore,
            "data": data,
            "gruppo": gruppo,
            "fruibile": fruibile,
            "scadenza": scadenza,
            "luogo": luogo
        })
    }

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
