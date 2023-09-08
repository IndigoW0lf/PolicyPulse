import pytest
from backend.database.models import CoSponsor, Bill, Politician
from backend.tests.factories.co_sponsor_factory import CoSponsorFactory
from backend.tests.factories.bill_factory import BillFactory
from backend.tests.factories.politician_factory import PoliticianFactory

@pytest.fixture
def politician(session):
    politician = PoliticianFactory(name="Test Politician")
    session.add(politician)
    session.commit()
    return politician

@pytest.fixture
def bill(session):
    bill = BillFactory(title="Test Bill")
    session.add(bill)
    session.commit()
    return bill

@pytest.fixture
def cosponsor(session, bill, politician):
    cosponsor = CoSponsorFactory(bill_id=bill.id, politician_id=politician.id)
    session.add(cosponsor)
    session.commit()
    return cosponsor

@pytest.fixture
def setup_cosponsor(cosponsor, bill, politician):
    return cosponsor, bill, politician

def test_cosponsor_creation(setup_cosponsor):
    cosponsor, _, _ = setup_cosponsor
    assert cosponsor is not None

def test_cosponsor_fields(setup_cosponsor):
    cosponsor, bill, politician = setup_cosponsor
    assert cosponsor.bill_id == bill.id
    assert cosponsor.politician_id == politician.id

@pytest.fixture
def session(db_session):
    yield db_session
    db_session.rollback()
