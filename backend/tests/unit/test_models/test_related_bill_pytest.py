import pytest
from backend.database.models import RelatedBill, Bill
from .conftest import create_related_bill, create_bill

def test_related_bill_creation(session):
    bill1 = create_bill(session)
    bill2 = create_bill(session, bill_number="HR002", title="Related Test Bill")
    related_bill = create_related_bill(session, bill_id=bill1.id, related_bill_id=bill2.id)
    assert related_bill is not None

def test_related_bill_fields(session):
    bill1 = create_bill(session)
    bill2 = create_bill(session, bill_number="HR002", title="Related Test Bill")
    related_bill = create_related_bill(session, bill_id=bill1.id, related_bill_id=bill2.id)
    
    assert related_bill.main_bill.title == bill1.title
    assert related_bill.related.title == bill2.title

def test_related_bill_relationship(session):
    bill1 = create_bill(session)
    bill2 = create_bill(session, bill_number="HR002", title="Related Test Bill")
    related_bill = create_related_bill(session, bill_id=bill1.id, related_bill_id=bill2.id)
    
    assert related_bill.main_bill.title == bill1.title
    assert related_bill.related.title == bill2.title
