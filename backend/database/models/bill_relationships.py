from backend import db

class BillRelationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=True)
    identified_by = db.Column(db.String, nullable=True)

    related_bill_id = db.Column(db.Integer, db.ForeignKey('related_bill.id'), nullable=False)
    related_bill = db.relationship('RelatedBill', back_populates='relationship_details', lazy=True)


    def __repr__(self):
        return f'<BillRelationship {self.id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "identified_by": self.identified_by,
            "related_bill_id": self.related_bill_id,
            "related_bill": self.related_bill.to_dict() if self.related_bill else None,
        }