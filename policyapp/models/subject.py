from policyapp import db

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Many-to-Many Relationship with Bill
    bills = db.relationship('Bill', secondary='Bill_subject', backref=db.backref('subjects', lazy=True))

# Association Table for Many-to-Many Relationship between Bill and Subject
Bill_subject = db.Table('Bill_subject',
    db.Column('Bill_id', db.Integer, db.ForeignKey('Bill.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)