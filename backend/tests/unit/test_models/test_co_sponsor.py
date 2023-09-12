import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.database.models import CoSponsor, Bill, Politician
from backend.tests.factories.co_sponsor_factory import CoSponsorFactory
from backend.tests.factories.bill_factory import BillFactory
from backend.tests.factories.politician_factory import PoliticianFactory

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

def test_co_sponsor_creation(co_sponsor_factory, bill_factory, politician_factory):
    logger.info("Starting test_co_sponsor_creation")
    bill = bill_factory(title="Test Bill")
    politician = politician_factory(name="Test Politician")
    co_sponsor = co_sponsor_factory(bill=bill, politician=politician)

    assert co_sponsor is not None
    assert co_sponsor.id is not None
    assert co_sponsor.bill_id == bill.id
    assert co_sponsor.politician_id == politician.id

    # Fetch the co_sponsor from the database and check the relationships
    fetched_co_sponsor = CoSponsor.query.get(co_sponsor.id)
    assert fetched_co_sponsor.bill.title == bill.title
    assert fetched_co_sponsor.politician.name == politician.name
    logger.info("Completed test_co_sponsor_creation")

def test_co_sponsor_field_validations(session, co_sponsor_factory):
    logger.info("Starting test_co_sponsor_field_validations")
    # Test that co_sponsor cannot be created with non-existent bill_id and politician_id
    with pytest.raises(IntegrityError):
        co_sponsor = co_sponsor_factory(bill_id=9999, politician_id=9999)
        session.add(co_sponsor)
        session.commit()

    session.rollback()
    logger.info("Completed test_co_sponsor_field_validations")

def test_co_sponsor_relationships(co_sponsor_factory, bill_factory, politician_factory):
    logger.info("Starting test_co_sponsor_relationships")
    bill = bill_factory(title="Test Bill")
    politician = politician_factory(name="Test Politician")
    co_sponsor = co_sponsor_factory(bill=bill, politician=politician)

    assert co_sponsor.bill == bill
    assert co_sponsor.politician == politician
    logger.info("Completed test_co_sponsor_relationships")