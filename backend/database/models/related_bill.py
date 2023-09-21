from backend import db

class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    congress = db.Column(db.String, nullable=False)
    number = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    action_date = db.Column(db.Date, nullable=True)
    action_text = db.Column(db.String, nullable=True)
    relationship_type = db.Column(db.String, nullable=True)
    identified_by = db.Column(db.String, nullable=True)


    relationship_details = db.relationship('BillRelationship', back_populates='related_bill', lazy=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    bill = db.relationship('Bill', back_populates='related_bills', lazy=True)



    def __repr__(self):
        return f'<RelatedBill {self.id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "congress": self.congress,
            "number": self.number,
            "type": self.type,
            "action_date": self.action_date,
            "action_text": self.action_text,
            "relationship_type": self.relationship_type,
            "identified_by": self.identified_by,
            "relationship_details": [relationship.to_dict() for relationship in self.relationship_details],
            "bill_id": self.bill_id,
            "bill": self.bill.to_dict() if self.bill else None,
        }