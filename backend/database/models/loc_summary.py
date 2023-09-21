from backend import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
import logging

loc_summary_association = db.Table(
    'loc_summary_association',
    db.Column('loc_summary_id', db.Integer, db.ForeignKey('loc_summary.id'), primary_key=True),
    db.Column('loc_summary_code_id', db.Integer, db.ForeignKey('loc_summary_code.id'), primary_key=True)
)

class LOCSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_code = db.Column(db.String, nullable=False)
    action_date = db.Column(db.Date, nullable=True)
    update_date = db.Column(db.DateTime, nullable=True, index=True)
    action_desc = db.Column(db.String, nullable=True)
    text = db.Column(db.Text, nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bill = db.relationship('Bill', back_populates='loc_summaries')  # Changed to 'loc_summaries'
    loc_summary_codes = db.relationship('LOCSummaryCode', secondary=loc_summary_association, back_populates='loc_summaries')

    def __repr__(self):
        return f'<LOCSummary id={self.id}, version_code={self.version_code}>'

    def to_dict(self):
        return {
            "id": self.id,
            "version_code": self.version_code,
            "action_date": self.action_date,
            "update_date": self.update_date,
            "action_desc": self.action_desc,
            "text": self.text,
            "bill_id": self.bill_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "loc_summary_codes": [loc_summary_code.id for loc_summary_code in self.loc_summary_codes],
        }


class LOCSummaryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chamber = db.Column(db.String, nullable=False)
    version_code = db.Column(db.String, nullable=False, unique=True)
    action_desc = db.Column(db.String, nullable=False)
    
    loc_summaries = db.relationship('LOCSummary', secondary=loc_summary_association, back_populates='loc_summary_codes')

    def __repr__(self):
        return f'<LOCSummaryCode {self.version_code} - {self.chamber}>'

    def to_dict(self):
        return {
            "id": self.id, 
            "version_code": self.version_code,
            "chamber": self.chamber,
            "action_desc": self.action_desc,
            "loc_summaries": [loc_summary.id for loc_summary in self.loc_summaries],
        }