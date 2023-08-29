from policyapp import db

class Legislation(db.Model):
    # 'Text' types may need to be updated later, but these may be csv, JSON, or other structured formats
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    date_introduced = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(100), nullable=True)
    bill_number = db.Column(db.String(50), nullable=False, unique=True)
    sponsor = db.Column(db.String(200), nullable=False)
    co_sponsors = db.Column(db.Text, nullable=True)  
    committee = db.Column(db.String(200), nullable=True)
    voting_record = db.Column(db.Text, nullable=True) 
    full_text_link = db.Column(db.String(500), nullable=True)
    related_bills = db.Column(db.Text, nullable=True) 
    tags = db.Column(db.String(300), nullable=True)  
    last_action_date = db.Column(db.Date, nullable=True)
    last_action_description = db.Column(db.Text, nullable=True)