import pytest
from datetime import date
from policyapp import create_app, db
from policyapp.models import Subject, Bill

@pytest.fixture(scope='module')
def new_subject():
    subject = Subject(name="Test Subject", description="This is a test subject.")
    bill = Bill(
        title="Test Bill",
        summary="This is a test summary",
        date_introduced=date.today(),
        status="Proposed",
        bill_number="HR001",
        sponsor_name="Test Sponsor",
        committee="Test Committee",
        voting_record="Yea: 10, Nay: 5",
        full_text_link="http://example.com/full_text",
        tags="Test, Bill",
        last_action_date=date.today(),
        last_action_description="Introduced in House",
        congress="117th",
        bill_type="House Bill",
        sponsor_id=1
    )
    subject.bills.append(bill)
    db.session.add_all([subject, bill])
    db.session.commit()

    return subject

def test_subject_creation(new_subject):
    assert new_subject is not None

def test_subject_fields(new_subject):
    assert new_subject.name == "Test Subject"
    assert new_subject.description == "This is a test subject."

def test_subject_relationship(new_subject):
    assert new_subject.bills[0].title == "Test Bill"