import pytest
from datetime import date
from backend.database.models import Subject

def test_subject_creation(init_database):
    session = init_database.session
    subject = session.query(Subject).first()
    assert subject is not None

def test_subject_fields(init_database):
    session = init_database.session
    subject = session.query(Subject).first()
    
    assert subject.name == "Test Subject"
    assert subject.description == "This is a test subject."

def test_subject_relationship(init_database):
    session = init_database.session
    subject = session.query(Subject).first()

    # Check if subject has associated bills
    if subject.bills:
        assert subject.bills[0].title == "Related Test Bill"
    else:
        assert False, "Subject has no associated bills"