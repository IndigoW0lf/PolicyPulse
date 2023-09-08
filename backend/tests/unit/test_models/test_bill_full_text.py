import pytest
from backend.database.models import BillFullText, Bill
from backend.tests.factories.bill_full_text_factory import BillFullTextFactory
from backend.tests.factories.bill_factory import BillFactory

@pytest.fixture
def bill(session):
    bill = BillFactory()
    session.add(bill)
    session.commit()
    return bill

@pytest.fixture
def bill_full_text(session, bill):
    bill_full_text = BillFullTextFactory(bill_id=bill.id)
    session.add(bill_full_text)
    session.commit()
    return bill_full_text

@pytest.fixture
def setup_bill_full_text(bill_full_text, session):
    return bill_full_text

def test_bill_full_text_creation(setup_bill_full_text):
    bill_full_text = setup_bill_full_text
    assert bill_full_text is not None

def test_field_validations(setup_bill_full_text):
    bill_full_text = setup_bill_full_text
    assert bill_full_text.title is None
    assert bill_full_text.meta_data is None
    assert bill_full_text.actions is None
    assert bill_full_text.sections is None

def test_foreign_keys(setup_bill_full_text):
    bill_full_text = setup_bill_full_text
    assert bill_full_text.bill_id is not None

def test_relationships(setup_bill_full_text, bill):
    bill_full_text = setup_bill_full_text
    assert bill_full_text.bill.title == bill.title

@pytest.fixture
def session(db_session):
    yield db_session
    db_session.rollback()
