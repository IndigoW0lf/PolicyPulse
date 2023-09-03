from policyapp import db

class LOCSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_code = db.Column(db.String(50), nullable=False)  # Represents the version of the bill (e.g., Introduced, Engrossed, Enrolled, etc.)
    chamber = db.Column(db.String(50), nullable=True)  # Chamber where the bill is introduced or currently resides (House or Senate)
    action_description = db.Column(db.String(200), nullable=False)  # Description of the action taken on this version of the bill
    summary_text = db.Column(db.Text, nullable=True)  # The actual summary text from the LOC

    # Relationship
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)