import time
import random
import csv
from datetime import datetime, timedelta
import threading

# Lista per memorizzare le ultime temperature
temperature_log = []

# Dati statici
struttura = "Ospedale San Giovanni"
sacche_ids = ["SAC001", "SAC002", "SAC003", "SAC004", "SAC005"]

# Funzione simulata per invio alla blockchain
def add_kv_to_blockchain(payload):
    print("Payload inviato alla blockchain:")
    print(payload)
    print("-" * 50)

# Funzione per salvare su CSV
def salva_su_csv():
    while True:
        time.sleep(60)
        now = datetime.now()
        cutoff = now - timedelta(hours=1)
        recent_data = [(t.strftime("%Y-%m-%d %H:%M:%S"), temp) for t, temp in temperature_log if t >= cutoff]

        with open("temperature_log.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["timestamp", "temperatura"])
            writer.writerows(recent_data)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] CSV aggiornato con {len(recent_data)} voci.")

# Thread per salvataggio su CSV ogni 60s
threading.Thread(target=salva_su_csv, daemon=True).start()

# Loop principale ogni 10 secondi
while True:
    now = datetime.now()
    temperatura_corrente = round(random.uniform(2.0, 6.0), 2)

    # Aggiungi temperatura e filtra vecchie
    temperature_log.append((now, temperatura_corrente))
    temperature_log = [(t, temp) for t, temp in temperature_log if now - t <= timedelta(hours=1)]

    # Calcola media
    media = round(sum(temp for _, temp in temperature_log) / len(temperature_log), 2)

    # Prepara payload
    payload = {
        "struttura": struttura,
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "sacche_riferite": random.sample(sacche_ids, k=random.randint(2, len(sacche_ids))),
        "temperatura_media_ultima_ora": media
    }

    # Invio simulato
    add_kv_to_blockchain(payload)

    time.sleep(10)
