from datetime import datetime
from policyapp import db

class TitleType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)