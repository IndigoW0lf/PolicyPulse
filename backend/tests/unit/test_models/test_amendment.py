import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.database.models import Amendment
from backend.tests.factories.amendment_factory import AmendmentFactory
from backend.tests.factories.bill_factory import BillFactory

logger = logging.getLogger(__name__)

@pytest.fixture
def bill_factory(session):
    def _bill_factory(**kwargs):
        bill = BillFactory(**kwargs)
        session.add(bill)
        session.commit()
        return bill
    return _bill_factory

@pytest.fixture
def amendment_factory(session):
    def _amendment_factory(**kwargs):
        amendment = AmendmentFactory(**kwargs)
        session.add(amendment)
        session.commit()
        return amendment
    return _amendment_factory

def test_amendment_creation(amendment_factory, bill_factory):
    logger.info("Starting test_amendment_creation")
    bill = bill_factory()
    amendment = amendment_factory(bill=bill)

    assert amendment is not None
    assert amendment.id is not None
    assert amendment.amendment_number is not None
    assert amendment.description.startswith('Amendment Description')
    assert amendment.date_proposed is not None
    assert isinstance(amendment.status)

    # Fetch the amendment from the database and check the relationships
    fetched_amendment = Amendment.query.get(amendment.id)
    assert fetched_amendment.bill.id == bill.id
    logger.info("Completed test_amendment_creation")

def test_amendment_field_validations(session, amendment_factory):
    logger.info("Starting test_amendment_field_validations")
    # Test that amendment_number cannot be null
    with pytest.raises(IntegrityError):
        amendment = amendment_factory(amendment_number=None)
        session.add(amendment)
        session.commit()

    session.rollback()
    # Add other field validation tests as necessary
    logger.info("Completed test_amendment_field_validations")

def test_amendment_foreign_keys(session, amendment_factory):
    logger.info("Starting test_amendment_foreign_keys")
    # Test that amendment cannot be created with non-existent bill_id
    with pytest.raises(IntegrityError):
        amendment = amendment_factory(bill_id=9999)
        session.add(amendment)
        session.commit()

    session.rollback()
    logger.info("Completed test_amendment_foreign_keys")

def test_amendment_relationships(amendment_factory, bill_factory):
    logger.info("Starting test_amendment_relationships")
    bill = bill_factory()
    amendment = amendment_factory(bill=bill)

    assert amendment.bill == bill
    logger.info("Completed test_amendment_relationships")