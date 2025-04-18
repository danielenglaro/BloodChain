import hashlib

def hash_with_salt(value, salt="Luca"):
    return hashlib.sha512((value + salt).encode()).hexdigest()