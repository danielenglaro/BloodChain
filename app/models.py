from . import db

class User(db.Model):
    __tablename__ = 'Users'
    Usrnm = db.Column(db.String(200), primary_key=True)
    Pwd = db.Column(db.String(200), primary_key=True)