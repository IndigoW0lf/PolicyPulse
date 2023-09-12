import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.database.models import RelatedBill, Bill
from backend.tests.factories.related_bill_factory import RelatedBillFactory
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
def related_bill_factory(session):
    def _related_bill_factory(**kwargs):
        related_bill = RelatedBillFactory(**kwargs)
        session.add(related_bill)
        session.commit()
        return related_bill
    return _related_bill_factory

def test_related_bill_creation(related_bill_factory, bill_factory):
    logger.info("Starting test_related_bill_creation")
    main_bill = bill_factory(title="Main Test Bill")
    related_bill_instance = bill_factory(title="Related Test Bill")
    related_bill = related_bill_factory(main_bill=main_bill, related_bill=related_bill_instance)

    assert related_bill is not None
    assert related_bill.id is not None
    assert related_bill.main_bill.title == main_bill.title
    assert related_bill.related_bill.title == related_bill_instance.title

    # Fetch the related_bill from the database and check the relationships
    fetched_related_bill = RelatedBill.query.get(related_bill.id)
    assert fetched_related_bill.main_bill.title == main_bill.title
    assert fetched_related_bill.related_bill.title == related_bill_instance.title
    logger.info("Completed test_related_bill_creation")

def test_related_bill_field_validations(session, related_bill_factory):
    logger.info("Starting test_related_bill_field_validations")
    # Test that related_bill cannot be created with null fields
    with pytest.raises(IntegrityError):
        related_bill = related_bill_factory(bill_id=None, related_bill_id=None)
        session.add(related_bill)
        session.commit()

    session.rollback()
    logger.info("Completed test_related_bill_field_validations")

def test_related_bill_relationships(related_bill_factory, bill_factory):
    logger.info("Starting test_related_bill_relationships")
    main_bill = bill_factory(title="Main Test Bill")
    related_bill_instance = bill_factory(title="Related Test Bill")
    related_bill = related_bill_factory(main_bill=main_bill, related_bill=related_bill_instance)

    # Testing the relationship between main_bill and related_bill
    assert related_bill.main_bill.title == main_bill.title
    assert related_bill.related_bill.title == related_bill_instance.title
    logger.info("Completed test_related_bill_relationships")
