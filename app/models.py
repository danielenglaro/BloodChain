from . import db

class Ospedale(db.Model):
    __tablename__ = 'Ospedali'
    Usrnm = db.Column(db.String(200), primary_key=True)
    Pwd = db.Column(db.String(200), primary_key=True)

class Donatore(db.Model):
    __tablename__ = 'Donatori'
    Usrnm = db.Column(db.String(200), primary_key=True)
    Pwd = db.Column(db.String(200), primary_key=True)