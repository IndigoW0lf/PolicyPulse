import pytest
from backend.database.models.subject import Subject
from backend.tests.factories.subject_factory import SubjectFactory
from backend.tests.factories.bill_factory import BillFactory
from backend import db

@pytest.fixture
def setup_subject(session):
    subject = SubjectFactory()
    session.add(subject)
    session.commit()
    return subject

def test_subject_creation(setup_subject):
    subject = setup_subject
    assert subject is not None

def test_subject_fields(setup_subject):
    subject = setup_subject
    assert subject.name == "Test Subject"
    assert subject.description == "This is a test subject."

def test_subject_relationship(session):
    subject = SubjectFactory()
    bill = BillFactory(bill_number="HR002", title="Related Test Bill")
    subject.bills.append(bill)
    session.add(subject)
    session.add(bill)
    session.commit()
    
    assert subject.bills[0].title == bill.title
