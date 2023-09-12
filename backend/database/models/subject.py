from backend import db

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    bills = db.relationship('Bill', secondary='bill_subject', back_populates='subjects', lazy=True)
    primary_bills = db.relationship('Bill', back_populates='primary_subject', lazy=True)


    def __repr__(self):
        return f'<Subject {self.name}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "bills": [bill.to_dict() for bill in self.bills],
            "primary_bills": [bill.to_dict() for bill in self.primary_bills],
        }

bill_subject = db.Table('bill_subject',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True, index=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True, index=True)
)