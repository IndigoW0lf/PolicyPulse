import pytest
from backend.database.models.related_bill import RelatedBill
from backend.tests.factories.related_bill_factory import RelatedBillFactory
from backend.tests.factories.bill_factory import BillFactory
from backend import db

@pytest.fixture
def setup_related_bill(session):
    bill1 = BillFactory()
    bill2 = BillFactory(bill_number="HR002", title="Related Test Bill")
    session.add(bill1)
    session.add(bill2)
    session.commit()
    
    related_bill = RelatedBillFactory(bill_id=bill1.id, related_bill_id=bill2.id)
    session.add(related_bill)
    session.commit()
    return related_bill, bill1, bill2

def test_related_bill_creation(setup_related_bill):
    related_bill, _, _ = setup_related_bill
    assert related_bill is not None

def test_related_bill_fields(setup_related_bill):
    related_bill, bill1, bill2 = setup_related_bill
    assert related_bill.main_bill.title == bill1.title
    assert related_bill.related.title == bill2.title

def test_related_bill_relationship(setup_related_bill):
    related_bill, bill1, bill2 = setup_related_bill
    assert related_bill.main_bill.title == bill1.title
    assert related_bill.related.title == bill2.title

@pytest.fixture
def session(db_session):
    yield db_session
    db_session.rollback()