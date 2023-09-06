import pytest
from backend.database.models import Committee
from .conftest import create_committee, create_bill

def test_committee_creation(session):
    committee = create_committee(session)
    assert committee is not None

def test_committee_fields(session):
    committee = create_committee(session, name="Test Committee", chamber="House", committee_code="TC001")
    assert committee.name == "Test Committee"
    assert committee.chamber == "House"
    assert committee.committee_code == "TC001"

def test_committee_relationship(session):
    committee = create_committee(session)
    bill = create_bill(session)
    committee.bills.append(bill)
    session.flush()
    
    assert committee.bills[0].title == bill.title
