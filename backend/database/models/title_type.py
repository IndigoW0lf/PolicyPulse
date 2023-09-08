from backend import db

class TitleType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=False)
    
    bills = db.relationship('Bill', back_populates='title_type', lazy=True)

    def __repr__(self):
        return f'<TitleType {self.code} - {self.description}>'