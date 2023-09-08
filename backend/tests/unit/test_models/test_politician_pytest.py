import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.database.models import Politician, Bill, CoSponsor
from backend.tests.factories.politician_factory import PoliticianFactory
from backend.tests.factories.bill_factory import BillFactory
from backend.tests.factories.co_sponsor_factory import CoSponsorFactory

logger = logging.getLogger(__name__)

@pytest.fixture
def politician_factory(session):
    def _politician_factory(**kwargs):
        politician = PoliticianFactory(**kwargs)
        session.add(politician)
        session.commit()
        return politician
    return _politician_factory

@pytest.fixture
def bill_factory(session):
    def _bill_factory(**kwargs):
        bill = BillFactory(**kwargs)
        session.add(bill)
        session.commit()
        return bill
    return _bill_factory

@pytest.fixture
def co_sponsor_factory(session):
    def _co_sponsor_factory(**kwargs):
        co_sponsor = CoSponsorFactory(**kwargs)
        session.add(co_sponsor)
        session.commit()
        return co_sponsor
    return _co_sponsor_factory

def test_politician_creation(politician_factory):
    logger.info("Starting test_politician_creation")
    politician = politician_factory(name="Test Politician", state="Test State", party="Test Party", role="Test Role", profile_link="http://example.com/profile")

    assert politician is not None
    assert politician.id is not None
    assert politician.name == "Test Politician"
    assert politician.state == "Test State"
    assert politician.party == "Test Party"
    assert politician.role == "Test Role"
    assert politician.profile_link == "http://example.com/profile"

    # Fetch the politician from the database and check the fields
    fetched_politician = Politician.query.get(politician.id)
    assert fetched_politician.name == politician.name
    assert fetched_politician.state == politician.state
    assert fetched_politician.party == politician.party
    assert fetched_politician.role == politician.role
    assert fetched_politician.profile_link == politician.profile_link
    logger.info("Completed test_politician_creation")

def test_politician_field_validations(session, politician_factory):
    logger.info("Starting test_politician_field_validations")
    # Test that politician cannot be created with null name
    with pytest.raises(IntegrityError):
        politician = politician_factory(name=None)
        session.add(politician)
        session.commit()

    session.rollback()
    logger.info("Completed test_politician_field_validations")

def test_politician_relationships(politician_factory, bill_factory, co_sponsor_factory):
    logger.info("Starting test_politician_relationships")
    politician = politician_factory(name="Test Politician")
    bill = bill_factory(title="Test Bill", sponsor=politician)
    co_sponsor = co_sponsor_factory(politician=politician, bill=bill)

    assert politician.sponsored_bills[0].title == bill.title
    assert co_sponsor.bill.title == bill.title
    logger.info("Completed test_politician_relationships")