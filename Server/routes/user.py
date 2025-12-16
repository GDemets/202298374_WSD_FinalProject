from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(30),unique=True, nullable=False)
    mail = db.Column(db.String(30),unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'pseudo': self.pseudo,
            'mail': self.mail,
            'password': self.password,
            'role': self.role
        }

