import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.database.models import BillFullText, Bill
from backend.tests.factories.bill_full_text_factory import BillFullTextFactory
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
def bill_full_text_factory(session):
    def _bill_full_text_factory(**kwargs):
        bill_full_text = BillFullTextFactory(**kwargs)
        session.add(bill_full_text)
        session.commit()
        return bill_full_text
    return _bill_full_text_factory

def test_bill_full_text_creation(bill_full_text_factory, bill_factory):
    logger.info("Starting test_bill_full_text_creation")
    bill = bill_factory()
    bill_full_text = bill_full_text_factory(bill=bill)

    assert bill_full_text is not None
    assert bill_full_text.id is not None
    assert bill_full_text.title.startswith('Bill Full Text Title')
    assert bill_full_text.bill_metadata is not None
    assert bill_full_text.actions is not None
    assert bill_full_text.sections is not None

    # Fetch the bill_full_text from the database and check the relationships
    fetched_bill_full_text = BillFullText.query.get(bill_full_text.id)
    assert fetched_bill_full_text.bill.id == bill.id
    logger.info("Completed test_bill_full_text_creation")

def test_bill_full_text_field_validations(session, bill_full_text_factory):
    logger.info("Starting test_bill_full_text_field_validations")
    # Test that title cannot be null (if necessary, add similar tests for other fields)
    with pytest.raises(IntegrityError):
        bill_full_text = bill_full_text_factory(title=None)
        session.add(bill_full_text)
        session.commit()

    session.rollback()
    logger.info("Completed test_bill_full_text_field_validations")

def test_bill_full_text_foreign_keys(session, bill_full_text_factory):
    logger.info("Starting test_bill_full_text_foreign_keys")
    # Test that bill_full_text cannot be created with non-existent bill_id
    with pytest.raises(IntegrityError):
        bill_full_text = bill_full_text_factory(bill_id=9999)
        session.add(bill_full_text)
        session.commit()

    session.rollback()
    logger.info("Completed test_bill_full_text_foreign_keys")

def test_bill_full_text_relationships(bill_full_text_factory, bill_factory):
    logger.info("Starting test_bill_full_text_relationships")
    bill = bill_factory()
    bill_full_text = bill_full_text_factory(bill=bill)

    assert bill_full_text.bill == bill
    logger.info("Completed test_bill_full_text_relationships")
