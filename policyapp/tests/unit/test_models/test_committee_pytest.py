import pytest
from policyapp import create_app, db
from policyapp.models import Committee, Bill

@pytest.fixture(scope='module')
def new_committee():
    committee = Committee(name="Test Committee", chamber="House", committee_code="TC001")
    bill = Bill(title="Test Bill", bill_number="HR001", sponsor_name="Test Politician")
    committee.bills.append(bill)
    db.session.add_all([committee, bill])
    db.session.commit()

    return committee

def test_committee_creation(new_committee):
    assert new_committee is not None

def test_committee_fields(new_committee):
    assert new_committee.name == "Test Committee"
    assert new_committee.chamber == "House"
    assert new_committee.committee_code == "TC001"

def test_committee_relationship(new_committee):
    assert new_committee.bills[0].title == "Test Bill"