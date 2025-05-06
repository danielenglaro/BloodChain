from . import db

class Ospedale(db.Model):
    __tablename__ = 'Ospedali'  # <- rispettare la maiuscola del nome tabella

    Usrnm = db.Column(db.String(200), primary_key=True)
    Pwd = db.Column(db.String(200), primary_key=True)
    Id = db.Column(db.Integer)

class Donatore(db.Model):
    __tablename__ = 'Donatori'

    CF = db.Column(db.String(200), primary_key=True)
    Pwd = db.Column(db.String(200), primary_key=True)
