import pytest
from datetime import date
from backend.database.models import Bill

def test_bill_creation(init_database):
    session = init_database.session
    bill = session.query(Bill).filter_by(bill_number="HR001").first()
    assert bill is not None

def test_field_validations(init_database):
    session = init_database.session
    bill = session.query(Bill).filter_by(bill_number="HR001").first()
    assert bill is not None
    assert bill.title == "Test Bill"
    assert bill.summary == "This is a test summary"
    assert bill.date_introduced is not None
    assert bill.status == "Proposed"
    assert bill.bill_number == "HR001"
    assert bill.sponsor_name == "Test Politician"

def test_foreign_keys(init_database):
    session = init_database.session
    bill = session.query(Bill).filter_by(bill_number="HR001").first()
    assert bill is not None
    assert bill.sponsor_id is not None

def test_relationships(init_database):
    session = init_database.session
    bill = session.query(Bill).filter_by(bill_number="HR001").first()
    assert bill is not None
    assert bill.sponsor.name == "Test Politician"