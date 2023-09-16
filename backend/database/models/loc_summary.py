from backend import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

loc_summary_association = db.Table(
    'loc_summary_association',
    db.Column('loc_summary_id', db.Integer, db.ForeignKey('loc_summary.id'), primary_key=True),
    db.Column('loc_summary_code_id', db.Integer, db.ForeignKey('loc_summary_code.id'), primary_key=True)
)

class LOCSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    versions = db.Column(db.JSON)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bill = db.relationship('Bill', back_populates='loc_summary')
    loc_summary_codes = db.relationship('LOCSummaryCode', secondary=loc_summary_association, back_populates='loc_summaries')

    def __repr__(self):
        return f'<LOCSummary id={self.id}, versions={self.versions}>'

    def to_dict(self):
        return {
            "id": self.id,
            "versions": self.versions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class LOCSummaryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_code = db.Column(db.String(50), nullable=False, unique=True)
    chamber = db.Column(db.String(50), nullable=False)
    action_desc = db.Column(db.String(200), nullable=False)
    
    loc_summaries = db.relationship('LOCSummary', secondary=loc_summary_association, back_populates='loc_summary_codes')

    def __repr__(self):
        return f'<LOCSummaryCode {self.version_code} - {self.chamber}>'

    def to_dict(self):
        return {
            "id": self.id, 
            "version_code": self.version_code,
            "chamber": self.chamber,
            "action_desc": self.action_desc,
            "loc_summaries": [loc_summary.to_dict() for loc_summary in self.loc_summaries],
        }
