import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.database.models import Bill, ActionType, Politician
from backend.tests.factories.bill_factory import BillFactory
from backend.tests.factories.action_type_factory import ActionTypeFactory
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
def action_type_factory(session):
    def _action_type_factory(**kwargs):
        action_type = ActionTypeFactory(**kwargs)
        session.add(action_type)
        session.commit()
        return action_type
    return _action_type_factory

@pytest.fixture
def bill_factory(session):
    def _bill_factory(**kwargs):
        bill = BillFactory(**kwargs)
        session.add(bill)
        session.commit()
        return bill
    return _bill_factory

def test_bill_creation(bill_factory, politician_factory, action_type_factory):
    logger.info("Starting test_bill_creation")
    politician = politician_factory(name="Test Politician")
    action_type = action_type_factory(description='Bill is introduced')
    bill = bill_factory(sponsor=politician, action_type=action_type, title="Test Bill", summary="This is a test bill", status="Proposed", bill_number="HR001")

    assert bill is not None
    assert bill.id is not None
    assert bill.title == "Test Bill"
    assert bill.summary == "This is a test bill"
    assert bill.status == "Proposed"
    assert bill.bill_number == "HR001"
    assert bill.sponsor_name == "Test Politician"

    # Fetch the bill from the database and check the relationships
    fetched_bill = Bill.query.get(bill.id)
    assert fetched_bill.sponsor.name == politician.name
    assert fetched_bill.action_type.description == action_type.description
    logger.info("Completed test_bill_creation")

def test_bill_field_validations(session, bill_factory):
    logger.info("Starting test_bill_field_validations")
    # Test that title cannot be null (if necessary, add similar tests for other fields)
    with pytest.raises(IntegrityError):
        bill = bill_factory(title=None)
        session.add(bill)
        session.commit()

    session.rollback()
    logger.info("Completed test_bill_field_validations")

def test_bill_foreign_keys(session, bill_factory):
    logger.info("Starting test_bill_foreign_keys")
    # Test that bill cannot be created with non-existent sponsor_id and action_type_id
    with pytest.raises(IntegrityError):
        bill = bill_factory(sponsor_id=9999, action_type_id=9999)
        session.add(bill)
        session.commit()

    session.rollback()
    logger.info("Completed test_bill_foreign_keys")

def test_bill_relationships(bill_factory, politician_factory, action_type_factory):
    logger.info("Starting test_bill_relationships")
    politician = politician_factory(name="Test Politician")
    action_type = action_type_factory(description='Bill is introduced')
    bill = bill_factory(sponsor=politician, action_type=action_type)

    assert bill.sponsor == politician
    assert bill.action_type == action_type
    logger.info("Completed test_bill_relationships")