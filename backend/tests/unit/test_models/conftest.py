import pytest
import logging
from datetime import date
from sqlalchemy.exc import IntegrityError
from backend import create_app, db
from backend.database.models import Action, ActionType, Amendment, Bill, BillFullText, Committee, CoSponsor, LOCSummary, Politician, RelatedBill, Subject, TitleType

logger = logging.getLogger(__name__)

def clean_database(db):
    for table in reversed(db.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    
def create_action(db, **kwargs):
    defaults = {
        "action_date": date.today(),
        "description": "Test Action Description",
        "chamber": "House",
        "bill_id": 1,  # Assuming the bill with ID 1 exists
        "action_type_id": 1  # Assuming the action type with ID 1 exists
    }
    defaults.update(kwargs)
    action = Action.query.filter_by(description=defaults['description']).first()
    if not action:
        action = Action(**defaults)
        db.add(action)
        db.flush()
    return action

def create_action_type(db, description):
    action_type = ActionType.query.filter_by(description=description).first()
    if not action_type:
        action_type = ActionType(description=description)
        db.add(action_type)
        db.flush()
    return action_type

def create_amendment(db, **kwargs):
    defaults = {
        "amendment_number": "A001",
        "description": "Test Amendment",
        "date_proposed": date.today(),
        "status": "Proposed",
        "bill_id": 1  # Assuming the bill with ID 1 exists
    }
    defaults.update(kwargs)
    amendment = Amendment.query.filter_by(amendment_number=defaults['amendment_number']).first()
    if not amendment:
        amendment = Amendment(**defaults)
        db.add(amendment)
        db.flush()
    return amendment

def create_bill(db, **kwargs):
    defaults = {
        "id": 1,
        "title": "Test Bill",
        "summary": "This is a test bill",
        "date_introduced": date.today(),
        "status": "Proposed",
        "bill_number": "HR001",
        "sponsor_name": "Test Politician",
        "sponsor_id": 123,
        "action_type_id": "Committee Review",
        "title_type_id": "HJ",
        "committee=": "Committee2",
        "voting_record": "Yea: 40, Nay: 9",
        "full_bill_link": "http://example.com/full_bill_1",
        "tags": "Test Bill",
        "last_action_date": date.today(),
        "last_action_description": "Introduced in House"
    }
    defaults.update(kwargs)
    bill = Bill.query.filter_by(bill_number=defaults['bill_number']).first()
    if not bill:
        bill = Bill(**defaults)
        db.add(bill)
        db.flush()
    return bill

def create_bill2(db, **kwargs):
    defaults = {
        "id": 2,
        "title": "Related Test Bill",
        "summary": "This is a test summary for Bill 2",
        "date_introduced": date.today(),
        "status": "Conference Committee",
        "bill_number": "HR002",
        "sponsor_name": "Test Politician",
        "sponsor_id": 123,
        "action_type_id": "House Vote",
        "title_type_id": "SJ",
        "committee=": "Committee1",
        "voting_record": "Yea: 10, Nay: 5",
        "full_bill_link": "http://example.com/full_bill_2",
        "tags": "Test Bill",
        "last_action_date": date.today(),
        "last_action_description": "Floor Consideration"
    }
    defaults.update(kwargs)
    bill2 = Bill.query.filter_by(bill_number=defaults['bill_number']).first()
    if not bill2:
        bill2 = Bill(**defaults)
        db.add(bill2)
        db.flush()
    return bill2

def create_bill_full_text(db, **kwargs):
    defaults = {
        "bill_id": 1,  # Assuming the bill with ID 1 exists
        "title": None,
        "bill_metadata": None,
        "actions": None,
        "sections": None
    }
    defaults.update(kwargs)
    bill_full_text = BillFullText.query.filter_by(bill_id=defaults['bill_id']).first()
    if not bill_full_text:
        bill_full_text = BillFullText(**defaults)
        db.add(bill_full_text)
        db.flush()
    return bill_full_text


def create_cosponsor(db, **kwargs):
    defaults = {
        "bill_id": 1,  # Assuming the bill with ID 1 exists
        "politician_id": 1  # Assuming the politician with ID 1 exists
    }
    defaults.update(kwargs)
    co_sponsor = CoSponsor.query.filter_by(bill_id=defaults['bill_id'], politician_id=defaults['politician_id']).first()
    if not co_sponsor:
        co_sponsor = CoSponsor(**defaults)
        db.add(co_sponsor)
        db.flush()
    return co_sponsor

def create_committee(db, **kwargs):
    defaults = {
        "name": "Test Committee",
        "chamber": "House",
        "committee_code": "TC001"
    }
    defaults.update(kwargs)
    committee = Committee.query.filter_by(committee_code=defaults['committee_code']).first()
    if not committee:
        committee = Committee(**defaults)
        db.add(committee)
        db.flush()
    return committee

def create_locsummary(db, **kwargs):
    defaults = {
        "version_code": "Introduced",
        "chamber": "House",
        "action_description": "Introduced in House",
        "summary_text": "This is a test summary",
        "bill_id": 1  # Assuming the bill with ID 1 exists
    }
    defaults.update(kwargs)
    loc_summary = LOCSummary.query.filter_by(version_code=defaults['version_code']).first()
    if not loc_summary:
        loc_summary = LOCSummary(**defaults)
        db.add(loc_summary)
        db.flush()
    return loc_summary

def create_politician(db, **kwargs):
    defaults = {
        "name": "Test Politician",
        "state": "Test State",
        "party": "Test Party",
        "role": "Test Role",
        "profile_link": "http://example.com/profile"
    }
    defaults.update(kwargs)
    politician = Politician.query.filter_by(name=defaults['name']).first()
    if not politician:
        politician = Politician(**defaults)
        db.add(politician)
        db.flush()
    return politician

def create_related_bill(db, **kwargs):
    defaults = {
        "bill_id": 1,  # Assuming the bill with ID 1 exists
        "related_bill_id": 2  # Assuming the related bill with ID 2 exists
    }
    defaults.update(kwargs)
    related_bill = RelatedBill.query.filter_by(bill_id=defaults['bill_id'], related_bill_id=defaults['related_bill_id']).first()
    if not related_bill:
        related_bill = RelatedBill(**defaults)
        db.add(related_bill)
        db.flush()
    return related_bill

def create_subject(db, **kwargs):
    defaults = {
        "name": "Test Subject",
        "description": "This is a test subject."
    }
    defaults.update(kwargs)
    subject = Subject.query.filter_by(name=defaults['name']).first()
    if not subject:
        subject = Subject(**defaults)
        db.add(subject)
        db.flush()
    return subject

def create_title_type(db, **kwargs):
    defaults = {
        "code": "HR",
        "description": "House Resolution"
    }
    defaults.update(kwargs)
    title_type = TitleType.query.filter_by(code=defaults['code']).first()
    if not title_type:
        title_type = TitleType(**defaults)
        db.add(title_type)
        db.flush()
    return title_type

@pytest.fixture(scope='session')
def init_database():
    app = create_app('testing')
    with app.app_context():
        db.session.rollback()  # Ensure session is in a clean state
        db.create_all()
        clean_database(db)

        try:
            nested_session = db.session.begin_nested()
            print("Nested session started")

            # Using factory functions to create objects
            action_type = create_action_type(db, description="Bill is introduced")
            politician = create_politician(db, name="Test Politician", state="Test State", party="Test Party", role="Test Role", profile_link="http://example.com/profile")
            title_type = create_title_type(db, code="HR", description="House Resolution")
            committee = create_committee(db, name="Test Committee", chamber="House", committee_code="TC001")
            bill = create_bill(db, id=1, title="Test Bill", summary="This is a test bill", date_introduced=date.today(), status="Proposed", bill_number="HR001", sponsor_name="Test Politician", sponsor_id=politician.id, action_type_id=action_type.id, title_type_id=title_type.id, committee="Committee1", voting_record="Yea: 10, Nay: 5", full_bill_link="http://example.com/full_bill_1", tags="Test Bill", last_action_date=date.today(), last_action_description="Introduced in House")
            bill2 = create_bill2(db, id=2, title="Related Test Bill", summary="This is a test summary for Bill 2", date_introduced=date.today(), status="Proposed", bill_number="HR002", sponsor_name="Test Politician", sponsor_id=politician.id, action_type_id=action_type.id, title_type_id=title_type.id, committee="Test Committee", voting_record="Yea: 8, Nay: 7", full_bill_link="http://example.com/full_text_2", tags="Test Bill 2", last_action_date=date.today(), last_action_description="Introduced in House")
            related_bill = create_related_bill(db, bill_id=bill.id, related_bill_id=bill2.id)
            action = create_action(db, action_date=date.today(), description="Test Action Description", chamber="House", bill_id=bill.id, action_type_id=action_type.id)
            amendment = create_amendment(db, amendment_number="A001", description="Test Amendment", date_proposed=date.today(), status="Proposed", bill_id=bill.id)
            co_sponsor = create_cosponsor(db, bill_id=bill.id, politician_id=politician.id)
            loc_summary = create_locsummary(db, version_code="Introduced", chamber="House", action_description="Introduced in House", summary_text="This is a test summary", bill_id=bill.id)
            subject = create_subject(db, name="Test Subject", description="This is a test subject.")
            bill_full_text = create_bill_full_text(db, bill_id=bill.id, title="XML Title", bill_metadata={"publisher": "XML Publisher", "date": "2023-01-03", "format": "XML Format", "language": "XML Language", "rights": "XML Rights"})


            print("About to commit nested session")
            nested_session.commit()
            print("Nested session committed")

        except (IntegrityError, Exception) as e:
            logger.exception("An error occurred during database setup: %s", e)
            db.session.rollback()
            print("Error occurred, rolling back session")
    
        return db

@pytest.fixture(scope='function')
def session(init_database):
    app = create_app('testing')
    with app.app_context():
        db = init_database
        db.session.begin_nested()
        yield db.session
        db.session.rollback()