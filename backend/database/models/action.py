from backend import db

action_actioncode = db.Table('action_actioncode',
        db.Column('action_id', db.Integer, db.ForeignKey('action.id'), primary_key=True),
        db.Column('action_code_id', db.Integer, db.ForeignKey('action_code.id'), primary_key=True)
    )

class Action(db.Model):
    """Model representing actions."""
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    is_latest = db.Column(db.Boolean, default=False)
    chamber = db.Column(db.Text, nullable=True)
    action_date = db.Column(db.Date, nullable=False)
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True, index=True)
    yea_votes = db.Column(db.Integer, nullable=True)
    nay_votes = db.Column(db.Integer, nullable=True)
    record_vote_number = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    action_type = db.relationship('ActionType', back_populates='actions', lazy=True)
    action_codes = db.relationship('ActionCode', secondary=action_actioncode, 
    back_populates='action_code_relations')
    bill = db.relationship('Bill', back_populates='actions')

    def __repr__(self):
        return f'<Action {self.id} on {self.action_date}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "bill_id": self.bill_id,
            "is_latest": self.is_latest,
            "chamber": self.chamber,
            "action_date": self.action_date,
            "action_type_id": self.action_type_id,
            "yea_votes": self.yea_votes,
            "nay_votes": self.nay_votes,
            "record_vote_number": self.record_vote_number,
            "description": self.description,
        }

class ActionCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    action_code_relations = db.relationship('Action', secondary=action_actioncode, back_populates='action_codes')

    def __repr__(self):
        return f'<ActionCode {self.code}: {self.description}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "description": self.description,
            "actions": [action.id for action in self.action_code_relations],
        }
