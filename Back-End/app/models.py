from . import db

class PaketBild(db.Model):
    __tablename__ = 'paket_bild'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paket_bild = db.Column(db.LargeBinary, nullable=False)  # bytea maps to LargeBinary
    paket_id = db.Column(db.String, nullable=False)  # varchar maps to String
    ausschnitt = db.Column(db.Boolean, nullable=False)  # bool maps to Boolean

    def __repr__(self):
        return f'<PaketBild {self.id}, Paket ID: {self.paket_id}>'
