import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.tests.factories.title_type_factory import TitleTypeFactory
from backend.tests.factories.bill_factory import BillFactory
from backend.database.models import TitleType, Bill

logger = logging.getLogger(__name__)

@pytest.fixture
def title_type_factory(session):
    def _title_type_factory(**kwargs):
        title_type = TitleTypeFactory(**kwargs)
        session.add(title_type)
        session.commit()
        return title_type
    return _title_type_factory

@pytest.fixture
def bill_factory(session):
    def _bill_factory(**kwargs):
        bill = BillFactory(**kwargs)
        session.add(bill)
        session.commit()
        return bill
    return _bill_factory

def test_title_type_creation(title_type_factory):
    logger.info("Starting test_title_type_creation")
    title_type = title_type_factory(code="HR", description="House Resolution")

    assert title_type is not None
    assert title_type.id is not None
    assert title_type.code == "HR"
    assert title_type.description == "House Resolution"

    # Fetch the title_type from the database and check the fields
    fetched_title_type = TitleType.query.get(title_type.id)
    assert fetched_title_type.code == title_type.code
    assert fetched_title_type.description == title_type.description
    logger.info("Completed test_title_type_creation")

def test_title_type_relationships(title_type_factory, bill_factory):
    logger.info("Starting test_title_type_relationships")
    title_type = title_type_factory(code="HR", description="House Resolution")
    bill = bill_factory(title="Test Bill", title_type=title_type)

    assert bill.title_type == title_type
    assert title_type.bills[0].title == bill.title
    logger.info("Completed test_title_type_relationships")

def test_field_validations(session, title_type_factory):
    logger.info("Starting test_field_validations")
    # Test that code and description cannot be null
    with pytest.raises(IntegrityError):
        title_type = title_type_factory(code=None)
        session.add(title_type)
        session.commit()

    session.rollback()

    with pytest.raises(IntegrityError):
        title_type = title_type_factory(description=None)
        session.add(title_type)
        session.commit()

    session.rollback()
    logger.info("Completed test_field_validations")