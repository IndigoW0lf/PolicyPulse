from backend import db

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    bills = db.relationship('Bill', secondary='bill_subject', back_populates='subjects', lazy=True)

    def __repr__(self):
        return f'<Subject {self.name}>'

bill_subject = db.Table('bill_subject',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True, index=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True, index=True)
)