import pytest
from policyapp import create_app, db
from policyapp.models import Politician, Bill, CoSponsor

@pytest.fixture(scope='module')
def new_politician():
    politician = Politician(name="Test Politician", state="Test State", party="Test Party", role="Test Role")
    bill = Bill(title="Test Bill", bill_number="HR001", sponsor_name="Test Politician")
    co_sponsor = CoSponsor()
    co_sponsor.bill = bill
    co_sponsor.politician = politician
    db.session.add_all([politician, bill, co_sponsor])
    db.session.commit()

    return politician

def test_politician_creation(new_politician):
    assert new_politician is not None

def test_politician_fields(new_politician):
    assert new_politician.name == "Test Politician"
    assert new_politician.state == "Test State"
    assert new_politician.party == "Test Party"
    assert new_politician.role == "Test Role"

def test_politician_relationship(new_politician):
    assert new_politician.co_sponsored_bills[0].bill.title == "Test Bill"