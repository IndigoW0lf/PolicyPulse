from backend import db

class RelatedBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    main_bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)  # References the main bill
    related_bill_number = db.Column(db.String, nullable=False, index=True)  # Bill number from the XML of the related bill
    
    # Additional fields to store information about the related bill
    title = db.Column(db.String, nullable=False)
    congress = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    latest_action_date = db.Column(db.Date, nullable=True)
    latest_action_text = db.Column(db.String, nullable=True)
    
    # Fields to store relationship details
    relationship_type = db.Column(db.String, nullable=True)
    relationship_identified_by = db.Column(db.String, nullable=True)

    bill = db.relationship('Bill', back_populates='related_bills', lazy=True)

    def __repr__(self):
        return f'<RelatedBill {self.id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "main_bill_id": self.main_bill_id,
            "related_bill_number": self.related_bill_number,
            "title": self.title,
            "congress": self.congress,
            "type": self.type,
            "latest_action_date": self.latest_action_date,
            "latest_action_text": self.latest_action_text,
            "relationship_type": self.relationship_type,
            "relationship_identified_by": self.relationship_identified_by,
        }