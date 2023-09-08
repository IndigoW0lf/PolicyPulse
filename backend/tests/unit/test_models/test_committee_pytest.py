import pytest
from backend.database.models import Committee, Bill
from backend.tests.factories.committee_factory import CommitteeFactory
from backend.tests.factories.bill_factory import BillFactory

@pytest.fixture
def bill(session):
    bill = BillFactory(title="Test Bill")
    session.add(bill)
    session.commit()
    return bill

@pytest.fixture
def committee(session):
    committee = CommitteeFactory(name="Test Committee", chamber="House", committee_code="TC001")
    session.add(committee)
    session.commit()
    return committee

@pytest.fixture
def setup_committee(committee):
    return committee

def test_committee_creation(setup_committee):
    committee = setup_committee
    assert committee is not None

def test_committee_fields(setup_committee):
    committee = setup_committee
    assert committee.name == "Test Committee"
    assert committee.chamber == "House"
    assert committee.committee_code == "TC001"

def test_committee_relationship(setup_committee, bill, session):
    committee = setup_committee
    committee.bills.append(bill)
    session.flush()
    
    assert committee.bills[0].title == bill.title
