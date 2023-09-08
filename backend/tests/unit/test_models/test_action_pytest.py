import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.tests.factories.action_factory import ActionFactory
from backend.tests.factories.bill_factory import BillFactory
from backend.tests.factories.action_type_factory import ActionTypeFactory
from backend.database.models import Action, ActionType, Bill

logger = logging.getLogger(__name__)

@pytest.fixture
def action_factory(session):
    def _action_factory(**kwargs):
        action = ActionFactory(**kwargs)
        session.add(action)
        session.commit()
        return action
    return _action_factory

@pytest.fixture
def bill_factory(session):
    def _bill_factory(**kwargs):
        bill = BillFactory(**kwargs)
        session.add(bill)
        session.commit()
        return bill
    return _bill_factory

@pytest.fixture
def action_type_factory(session):
    def _action_type_factory(**kwargs):
        action_type = ActionTypeFactory(**kwargs)
        session.add(action_type)
        session.commit()
        return action_type
    return _action_type_factory

def test_action_creation(action_factory, bill_factory, action_type_factory):
    logger.info("Starting test_action_creation")
    bill = bill_factory()
    action_type = action_type_factory()
    action = action_factory(bill=bill, action_type=action_type)

    assert action is not None
    assert action.id is not None
    assert action.description.startswith('Action Description')
    assert action.chamber in ['House', 'Senate']
    assert action.action_date is not None
    assert action.bill_id == bill.id
    assert action.action_type_id == action_type.id

    # Fetch the action from the database and check the relationships
    fetched_action = Action.query.get(action.id)
    assert fetched_action.bill.id == bill.id
    assert fetched_action.action_type.id == action_type.id
    logger.info("Completed test_action_creation")


def test_action_relationships(action_factory, bill_factory, action_type_factory):
    logger.info("Starting test_action_relationships")
    bill = bill_factory()
    action_type = action_type_factory()
    action = action_factory(bill=bill, action_type=action_type)

    assert action.bill == bill
    assert action.action_type == action_type
    logger.info("Completed test_action_relationships")

def test_field_validations(session, action_factory):
    logger.info("Starting test_field_validations")
    # Test that action_date cannot be null
    with pytest.raises(IntegrityError):
        action = action_factory(action_date=None)
        session.add(action)
        session.commit()

    session.rollback()
    logger.info("Completed test_field_validations")

def test_foreign_keys(session, action_factory, bill_factory, action_type_factory):
    logger.info("Starting test_foreign_keys")
    # Test that action cannot be created with non-existent bill_id
    with pytest.raises(IntegrityError):
        action = action_factory(bill_id=9999)
        session.add(action)
        session.commit()

    session.rollback()

    # Test that action cannot be created with non-existent action_type_id
    with pytest.raises(IntegrityError):
        action = action_factory(action_type_id=9999)
        session.add(action)
        session.commit()

    session.rollback()
    logger.info("Completed test_foreign_keys")

def test_relationships(session, action_factory, bill_factory, action_type_factory):
    logger.info("Starting test_relationships")
    bill = bill_factory()
    action_type = action_type_factory()
    action = action_factory(bill=bill, action_type=action_type)

    # Test the relationship between Action and Bill
    assert action in bill.actions

    # Test the relationship between Action and ActionType
    assert action in action_type.actions
    logger.info("Completed test_relationships")