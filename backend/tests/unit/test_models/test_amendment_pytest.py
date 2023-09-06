import pytest
from datetime import date
from backend.database.models import Amendment
from .conftest import create_amendment, create_bill

def test_amendment_creation(session):
    bill = create_bill(session)
    amendment = create_amendment(session, bill_id=bill.id, amendment_number="A001")
    assert amendment is not None

def test_field_validations(session):
    bill = create_bill(session)
    amendment = create_amendment(session, bill_id=bill.id, amendment_number="A001", description="Test Amendment", date_proposed=date.today(), status="Proposed")
    assert amendment.amendment_number == "A001"
    assert amendment.description == "Test Amendment"
    assert amendment.date_proposed == date.today()
    assert amendment.status == "Proposed"

def test_foreign_keys(session):
    bill = create_bill(session)
    amendment = create_amendment(session, bill_id=bill.id, amendment_number="A001")
    assert amendment.bill_id is not None

def test_relationships(session):
    bill = create_bill(session, title="Test Bill")
    amendment = create_amendment(session, bill_id=bill.id, amendment_number="A001")
    assert amendment.bill.title == "Test Bill"
