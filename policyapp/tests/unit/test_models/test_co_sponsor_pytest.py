import pytest
from policyapp import create_app, db
from policyapp.models import CoSponsor, Bill, Politician

@pytest.fixture(scope='module')
def new_cosponsor():
    politician = Politician(name="Test Politician")
    bill = Bill(title="Test Bill", bill_number="HR001", sponsor_name="Test Politician")
    db.session.add_all([politician, bill])
    db.session.commit()

    cosponsor = CoSponsor(bill_id=bill.id, politician_id=politician.id)
    db.session.add(cosponsor)
    db.session.commit()

    return cosponsor

def test_cosponsor_creation(new_cosponsor):
    assert new_cosponsor is not None

def test_cosponsor_fields(new_cosponsor):
    assert new_cosponsor.bill_id is not None
    assert new_cosponsor.politician_id is not None
