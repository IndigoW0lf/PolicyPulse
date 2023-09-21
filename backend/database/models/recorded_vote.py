from backend import db

class RecordedVote(db.Model):
    __tablename__ = 'recorded_vote'
    id = db.Column(db.Integer, primary_key=True)
    chamber = db.Column(db.String, nullable=True)
    congress = db.Column(db.String, nullable=True)
    date = db.Column(db.Date, nullable=True)
    full_action_name = db.Column(db.String, nullable=True)
    roll_number = db.Column(db.String, nullable=True)
    session_number = db.Column(db.String, nullable=True)
    url = db.Column(db.String, nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    
    bill = db.relationship('Bill', back_populates='recorded_votes', lazy=True)

    def __repr__(self):
        return f'<RecordedVote {self.id} - {self.date} in {self.chamber}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "chamber": self.chamber,
            "congress": self.congress,
            "date": self.date,
            "full_action_name": self.full_action_name,
            "roll_number": self.roll_number,
            "session_number": self.session_number,
            "url": self.url,
            "bill_id": self.bill_id,
            "bill": self.bill.id if self.bill else None,
        }