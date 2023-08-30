from policyapp import db

class LOCSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_code = db.Column(db.String(50), nullable=False)
    chamber = db.Column(db.String(50), nullable=True)
    action_description = db.Column(db.String(200), nullable=False)
    bills = db.relationship('Legislation', backref='loc_summary', lazy=True)