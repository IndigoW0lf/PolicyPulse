import pytest
from backend.database.models.politician import Politician
from backend.tests.factories.politician_factory import PoliticianFactory
from backend.tests.factories.bill_factory import BillFactory
from backend.tests.factories.co_sponsor_factory import CoSponsorFactory
from backend import db

@pytest.fixture
def setup_politician(session):
    politician = PoliticianFactory(name="Test Politician", state="Test State", party="Test Party", role="Test Role", profile_link="http://example.com/profile")
    session.add(politician)
    session.commit()
    return politician

def test_politician_creation(setup_politician):
    politician = setup_politician
    assert politician is not None

def test_politician_fields(setup_politician):
    politician = setup_politician
    assert politician.name == "Test Politician"
    assert politician.state == "Test State"
    assert politician.party == "Test Party"
    assert politician.role == "Test Role"
    assert politician.profile_link == "http://example.com/profile"

def test_politician_sponsored_bills_relationship(session, setup_politician):
    politician = setup_politician
    bill = BillFactory(sponsor_id=politician.id, title="Test Bill")
    session.add(bill)
    session.commit()
    assert politician.sponsored_bills[0].title == bill.title

def test_politician_co_sponsored_bills_relationship(session, setup_politician):
    politician = setup_politician
    bill = BillFactory(title="Test Bill")
    cosponsor = CoSponsorFactory(bill_id=bill.id, politician_id=politician.id)
    session.add(bill)
    session.add(cosponsor)
    session.commit()
    assert cosponsor.bill.title == bill.title

@pytest.fixture
def session(db_session):
    yield db_session
    db_session.rollback()