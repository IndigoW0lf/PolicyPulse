from backend import db
from backend.database.models.committee import bill_committee
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import JSON
from backend import db 
from datetime import datetime
from backend.database.models.subcommittee import bill_subcommittee


class ActionType(db.Model):
    """Model representing action types."""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False, unique=True)
    is_latest = db.Column(db.Boolean, default=False)
    action_type = db.Column(db.String, nullable=False)
    
    actions = db.relationship('Action', back_populates='action_type', lazy=True)
    bills = db.relationship('Bill', back_populates='action_type')


action_actioncode = db.Table('action_actioncode',
        db.Column('action_id', db.Integer, db.ForeignKey('action.id'), primary_key=True),
        db.Column('action_code_id', db.Integer, db.ForeignKey('action_code.id'), primary_key=True)
    )

class Action(db.Model):
    """Model representing actions."""
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    action_date = db.Column(db.Date, nullable=False)
    chamber = db.Column(db.Text, nullable=True)
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True, index=True)
    is_latest = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    
    action_type = db.relationship('ActionType', back_populates='actions', lazy=True)
    action_codes = db.relationship('ActionCode', secondary=action_actioncode, 
    back_populates='action_code_relations')
    bill = db.relationship('Bill', back_populates='actions')

class ActionCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    action_code_relations = db.relationship('Action', secondary=action_actioncode, back_populates='action_codes')


class Amendment(db.Model):
    """Model representing amendments to bills."""
    id = db.Column(db.Integer, primary_key=True)
    amendment_number = db.Column(db.String(50), nullable=False)
    congress = db.Column(db.String(50), nullable=True)
    latest_action_date = db.Column(db.Date, nullable=True)
    latest_action_text = db.Column(db.Text, nullable=True)
    type = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=True)
    description = db.Column(db.Text, nullable=True)
    purpose = db.Column(db.Text, nullable=True)

    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=True)

    sponsor = db.relationship('Politician', back_populates='sponsored_amendments', lazy=True)
    bill = db.relationship('Bill', back_populates='amendments', lazy=True)
    actions = db.relationship('AmendmentAction', back_populates='amendment', lazy=True)
    amended_bill = db.relationship('AmendedBill', back_populates='amendment', lazy=True)
    links = db.relationship('AmendmentLink', back_populates='amendment', lazy=True)

class AmendmentAction(db.Model):
    """Model representing actions on amendments."""
    id = db.Column(db.Integer, primary_key=True)
    action_code = db.Column(db.String(50), nullable=True)
    action_date = db.Column(db.Date, nullable=True)
    action_time = db.Column(db.String(20), nullable=True)
    committee_name = db.Column(db.String(200), nullable=True)
    committee_system_code = db.Column(db.String(50), nullable=True)
    action_text = db.Column(db.Text, nullable=True)
    
    amendment_id = db.Column(db.Integer, db.ForeignKey('amendment.id'), nullable=False)
    amendment = db.relationship('Amendment', back_populates='actions')

class AmendedBill(db.Model):
    """Model representing bills amended by amendments."""
    id = db.Column(db.Integer, primary_key=True)
    congress = db.Column(db.String(50), nullable=True)
    origin_chamber = db.Column(db.String(255), nullable=True)
    origin_chamber_code = db.Column(db.String(30), nullable=True)
    title = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=True)
    
    amendment_id = db.Column(db.Integer, db.ForeignKey('amendment.id'), nullable=False)
    amendment = db.relationship('Amendment', back_populates='amended_bill')


class AmendmentLink(db.Model):
    """Model representing links related to amendments."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    
    amendment_id = db.Column(db.Integer, db.ForeignKey('amendment.id'), nullable=False)
    amendment = db.relationship('Amendment', back_populates='links')


class BillFullText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    title = db.Column(db.Text, nullable=True)
    raw_data = db.Column(db.Text, nullable=True)
    bill_metadata = db.Column(db.JSON, nullable=True)
    actions = db.Column(db.JSON, nullable=True)
    sections = db.Column(db.JSON, nullable=True)
    parsing_status = db.Column(db.String(50), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bill = db.relationship('Bill', back_populates='full_texts', lazy=True)


class BillTitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    title_type = db.Column(db.String, nullable=False)
    title_text = db.Column(db.String, nullable=False)
    chamber_code = db.Column(db.String, nullable=True)
    chamber_name = db.Column(db.String, nullable=True)
    
    bill = db.relationship('Bill', back_populates='titles')


class Bill(db.Model):
    """Model representing bills."""
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    date_introduced = db.Column(db.Date, nullable=False)
    origin_chamber = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String, nullable=False, index=True)
    bill_type = db.Column(db.String(255), nullable=True)
    congress = db.Column(db.String(255), nullable=True)
    committee = db.Column(db.String(255), nullable=True)
    last_action_date = db.Column(db.Date, nullable=True)                
    last_action_description = db.Column(db.Text, nullable=True)
    update_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of record creation
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)  # Timestamp of last update
    tags = db.Column(db.String, nullable=True, index=True)
    full_bill_link = db.Column(db.String(255), nullable=True)
    voting_record = db.Column(db.Text, nullable=True)
    xml_content = db.Column(JSON, nullable=True)  # Store the XML content as a JSON object
    
    action_type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'), nullable=True)
    primary_subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False)
    
    # Relationships
    action_type = db.relationship('ActionType', back_populates='bills', lazy=True)
    actions = db.relationship('Action', back_populates='bill', lazy=True)
    amendments = db.relationship('Amendment', back_populates='bill', lazy=True)
    co_sponsors = db.relationship('CoSponsor', back_populates='bill', lazy=True)
    committees = db.relationship('Committee', secondary=bill_committee, back_populates='bills')
    subcommittees = db.relationship('Subcommittee', secondary=bill_subcommittee, back_populates='bills', lazy=True)
    full_texts = db.relationship('BillFullText', back_populates='bill', lazy=True)
    laws = db.relationship('Law', back_populates='bill', lazy=True)
    loc_summaries = db.relationship('LOCSummary', back_populates='bill', lazy=True)  # Changed attribute name to 'loc_summaries' and removed uselist parameter
    notes = db.relationship('Note', back_populates='bill', lazy=True)
    policy_areas = db.relationship('PolicyArea', back_populates='bill', lazy=True)
    primary_subject = db.relationship('Subject', back_populates='primary_bills', lazy=True)
    recorded_votes = db.relationship('RecordedVote', back_populates='bill', lazy=True)
    related_bills = db.relationship('RelatedBill', back_populates='bill', lazy=True)
    sponsor = db.relationship('Politician', back_populates='sponsored_bills', lazy=True)
    subjects = db.relationship('Subject', secondary='bill_subject', back_populates='bills', lazy=True)
    titles = db.relationship('BillTitle', back_populates='bill', lazy=True)



class CoSponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'), nullable=False, index=True)
    sponsorship_date = db.Column(db.Date, nullable=True)  # New field to track the date of co-sponsorship
    is_original_cosponsor = db.Column(db.Boolean, nullable=True)  
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of record creation
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)  # Timestamp of last update
    sponsorship_withdrawn_date = db.Column(db.Date, nullable=True) 

    bill = db.relationship('Bill', back_populates='co_sponsors', lazy=True)
    politician = db.relationship('Politician', back_populates='co_sponsored_bills', lazy=True)


class Committee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    chamber = db.Column(db.String(255), nullable=False)
    committee_code = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bills = db.relationship('Bill', secondary='bill_committee', back_populates='committees', lazy=True)
    subcommittees = db.relationship('Subcommittee', backref='committee', lazy=True)


bill_committee = db.Table('bill_committee',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True),
    db.Column('committee_id', db.Integer, db.ForeignKey('committee.id'), primary_key=True)
)

class Law(db.Model):
    __tablename__ = 'law'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(255), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bill = db.relationship('Bill', back_populates='laws', lazy=True)


loc_summary_association = db.Table(
    'loc_summary_association',
    db.Column('loc_summary_id', db.Integer, db.ForeignKey('loc_summary.id'), primary_key=True),
    db.Column('loc_summary_code_id', db.Integer, db.ForeignKey('loc_summary_code.id'), primary_key=True)
)

class LOCSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_code = db.Column(db.String(255), nullable=False)
    action_date = db.Column(db.Date, nullable=True)
    update_date = db.Column(db.DateTime, nullable=True, index=True)
    action_desc = db.Column(db.String, nullable=True)
    text = db.Column(db.Text, nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    bill = db.relationship('Bill', back_populates='loc_summaries')  # Changed to 'loc_summaries'
    loc_summary_codes = db.relationship('LOCSummaryCode', secondary=loc_summary_association, back_populates='loc_summaries')


class LOCSummaryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_code = db.Column(db.String(50), nullable=False, unique=True)
    chamber = db.Column(db.String(50), nullable=False)
    action_desc = db.Column(db.String(200), nullable=False)
    
    loc_summaries = db.relationship('LOCSummary', secondary=loc_summary_association, back_populates='loc_summary_codes')


class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    
    bill = db.relationship('Bill', back_populates='notes', lazy=True)


class PolicyArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    bill = db.relationship('Bill', back_populates='policy_areas', lazy=True)


class Politician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True) 
    first_name = db.Column(db.String(255), nullable=True) 
    last_name = db.Column(db.String(255), nullable=True) 
    state = db.Column(db.String(30), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    party = db.Column(db.String(40), nullable=True)
    profile_link = db.Column(db.String(500), nullable=True)
    bioguide_id = db.Column(db.String(50), nullable=True)

    sponsored_amendments = db.relationship('Amendment', back_populates='sponsor', lazy=True)
    sponsored_bills = db.relationship('Bill', back_populates='sponsor', lazy=True)
    co_sponsored_bills = db.relationship('CoSponsor', back_populates='politician', lazy=True)


class RecordedVote(db.Model):
    __tablename__ = 'recorded_vote'
    id = db.Column(db.Integer, primary_key=True)
    chamber = db.Column(db.String(255), nullable=True)
    congress = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=True)
    full_action_name = db.Column(db.String(1000), nullable=True)
    roll_number = db.Column(db.String(255), nullable=True)
    session_number = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)
    
    bill = db.relationship('Bill', back_populates='recorded_votes', lazy=True)


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




class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False, unique=True)
    
    bills = db.relationship('Bill', secondary='bill_subject', back_populates='subjects', lazy=True)
    primary_bills = db.relationship('Bill', back_populates='primary_subject', lazy=True)


bill_subject = db.Table('bill_subject',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id'), primary_key=True, index=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True, index=True)
)
class VetoMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=True)
    message = db.Column(db.Text, nullable=True)
    president = db.Column(db.String(200), nullable=True)
    text = db.Column(db.Text, nullable=True)
    
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False, index=True)

