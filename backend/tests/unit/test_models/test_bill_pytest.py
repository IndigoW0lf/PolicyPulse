import pytest
from datetime import date
from backend.database.models import Bill
from .conftest import create_bill, create_politician

def test_bill_creation(session):
    bill = create_bill(session, bill_number="HR001")
    assert bill is not None

def test_field_validations(session):
    politician = create_politician(session, name="Test Politician")
    bill = create_bill(session, bill_number="HR001", title="Test Bill", summary="This is a test bill", date_introduced=date.today(), status="Proposed", sponsor_name="Test Politician", sponsor_id=politician.id)
    assert bill is not None
    assert bill.title == "Test Bill"
    assert bill.summary == "This is a test bill"
    assert bill.date_introduced == date.today()
    assert bill.status == "Proposed"
    assert bill.bill_number == "HR001"
    assert bill.sponsor_name == "Test Politician"

def test_foreign_keys(session):
    politician = create_politician(session, name="Test Politician")
    bill = create_bill(session, bill_number="HR001", sponsor_id=politician.id)
    assert bill is not None
    assert bill.sponsor_id is not None

def test_relationships(session):
    politician = create_politician(session, name="Test Politician")
    bill = create_bill(session, bill_number="HR001", sponsor_id=politician.id)
    assert bill is not None
    assert bill.sponsor.name == "Test Politician"
