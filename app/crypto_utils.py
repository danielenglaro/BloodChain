import os
import json
import base64
import secrets
import string
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

KEY_FILE = "secret_key.json"
KEY_VALIDITY_DAYS = 7

def load_or_generate_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            data = json.load(f)
            key_date = datetime.strptime(data["date"], "%Y-%m-%d")
            if datetime.now() - key_date < timedelta(days=KEY_VALIDITY_DAYS):
                return base64.b64decode(data["key"])

    # Genera nuova chiave
    key = os.urandom(32)
    with open(KEY_FILE, "w") as f:
        json.dump({
            "key": base64.b64encode(key).decode("utf-8"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }, f)
    return key

def encrypt_data(data_dict, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    data = json.dumps(data_dict).encode('utf-8')
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len] * pad_len)

    ciphertext = encryptor.update(data) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def decrypt_data(encrypted_str, key):
    try:
        raw = base64.b64decode(encrypted_str)
        iv, ciphertext = raw[:16], raw[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        pad_len = padded_data[-1]
        return json.loads(padded_data[:-pad_len])
    except Exception:
        return None  # Decifrazione fallita

def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Optional: ensure it includes at least one of each character type
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in string.punctuation for c in password)):
            return password