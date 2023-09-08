import pytest
from datetime import date
from backend.database.models import Bill, Politician
from backend.tests.factories.bill_factory import BillFactory
from backend.tests.factories.politician_factory import PoliticianFactory

@pytest.fixture
def politician(session):
    politician = PoliticianFactory(name="Test Politician")
    session.add(politician)
    session.commit()
    return politician

@pytest.fixture
def bill(session, politician):
    bill = BillFactory(sponsor_id=politician.id, sponsor_name=politician.name)
    session.add(bill)
    session.commit()
    return bill

@pytest.fixture
def setup_bill(bill, politician):
    return bill, politician

def test_bill_creation(setup_bill):
    bill, _ = setup_bill
    assert bill is not None

def test_field_validations(setup_bill):
    bill, _ = setup_bill
    assert bill.title == "Test Bill"
    assert bill.summary == "This is a test bill"
    assert bill.date_introduced == date.today()
    assert bill.status == "Proposed"
    assert bill.bill_number == "HR001"
    assert bill.sponsor_name == "Test Politician"

def test_foreign_keys(setup_bill):
    bill, _ = setup_bill
    assert bill.sponsor_id is not None

def test_relationships(setup_bill):
    bill, politician = setup_bill
    assert bill.sponsor.name == politician.name

@pytest.fixture
def session(db_session):
    yield db_session
    db_session.rollback()