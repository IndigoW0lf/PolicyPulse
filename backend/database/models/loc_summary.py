from backend import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


class LOCSummaryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_code = db.Column(db.String(50), nullable=False, unique=True)
    chamber = db.Column(db.String(50), nullable=False)
    action_desc = db.Column(db.String(200), nullable=False)
    
    loc_summaries = db.relationship('LOCSummary', back_populates='loc_summary_code', lazy=True)

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

class LOCSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    versions = db.Column(db.JSON)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LOCSummary id={self.id}, versions={self.versions}>'

    def to_dict(self):
        return {
            "id": self.id,
            "versions": self.versions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }