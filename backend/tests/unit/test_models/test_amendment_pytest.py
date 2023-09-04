import pytest
from datetime import date
from backend.database.models import Amendment

def test_amendment_creation(init_database):
    session = init_database.session
    amendment = session.query(Amendment).filter_by(amendment_number="A001").first()
    assert amendment is not None

def test_field_validations(init_database):
    session = init_database.session
    amendment = session.query(Amendment).filter_by(amendment_number="A001").first()
    assert amendment.amendment_number == "A001"
    assert amendment.description == "Test Amendment"
    assert amendment.date_proposed == date.today()
    assert amendment.status == "Proposed"

def test_foreign_keys(init_database):
    session = init_database.session
    amendment = session.query(Amendment).filter_by(amendment_number="A001").first()
    assert amendment.bill_id is not None

def test_relationships(init_database):
    session = init_database.session
    amendment = session.query(Amendment).filter_by(amendment_number="A001").first()
    assert amendment.bill.title == "Test Bill"