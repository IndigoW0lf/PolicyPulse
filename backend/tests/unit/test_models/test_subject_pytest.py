import pytest
from backend.database.models import Subject
from .conftest import create_subject, create_bill

def test_subject_creation(session):
    subject = create_subject(session)
    assert subject is not None

def test_subject_fields(session):
    subject = create_subject(session, name="Test Subject", description="This is a test subject.")
    assert subject.name == "Test Subject"
    assert subject.description == "This is a test subject."

def test_subject_relationship(session):
    subject = create_subject(session)
    bill = create_bill(session, bill_number="HR002", title="Related Test Bill")
    subject.bills.append(bill)
    session.flush()
    
    assert subject.bills[0].title == bill.title
