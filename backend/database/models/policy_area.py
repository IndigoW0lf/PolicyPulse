from backend import db

class PolicyArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    bill = db.relationship('Bill', back_populates='policy_areas', lazy=True)

    def __repr__(self):
        return f'<PolicyArea {self.name}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "bill_id": self.bill_id,
            "bill": self.bill.to_dict() if self.bill else None,
        }