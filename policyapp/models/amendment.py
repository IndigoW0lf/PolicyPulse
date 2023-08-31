from policyapp import db

class Amendment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amendment_number = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_proposed = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(100), nullable=True)
    
    # Foreign Key to Bill
    Bill_id = db.Column(db.Integer, db.ForeignKey('Bill.id'), nullable=False)
    
    # Relationship with Bill
    Bill = db.relationship('Bill', backref=db.backref('amendments', lazy=True))
