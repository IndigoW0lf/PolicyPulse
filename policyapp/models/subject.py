from policyapp import db

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Many-to-Many Relationship with Bill
    bills = db.relationship('Bill', secondary='bill_subject', backref=db.backref('subjects', lazy=True))

# Association Table for Many-to-Many Relationship between Bill and Subject
bill_subject = db.Table('bill_subject',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)