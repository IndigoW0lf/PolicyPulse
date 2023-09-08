import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.database.models import Action, Bill, ActionType
from backend.tests.factories import ActionFactory, BillFactory, ActionTypeFactory

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

def test_action_type_creation(action_type_factory):
    logger.info("Starting test_action_type_creation")
    action_type = action_type_factory()
    
    assert action_type is not None
    assert action_type.id is not None
    assert action_type.description.startswith('Action Type Description')
    
    # Fetch the action_type from the database and check the attributes
    fetched_action_type = ActionType.query.get(action_type.id)
    assert fetched_action_type.description == action_type.description
    logger.info("Completed test_action_type_creation")

def test_action_type_relationships(action_type_factory, action_factory, bill_factory):
    logger.info("Starting test_action_type_relationships")
    action_type = action_type_factory()
    action = action_factory(action_type=action_type)
    bill = bill_factory(action_type=action_type)
    
    assert action in action_type.actions
    assert bill in action_type.bills
    logger.info("Completed test_action_type_relationships")

def test_action_type_field_validations(session, action_type_factory):
    logger.info("Starting test_action_type_field_validations")
    # Test that description cannot be null
    with pytest.raises(IntegrityError):
        action_type = action_type_factory(description=None)
        session.add(action_type)
        session.commit()

    session.rollback()
    logger.info("Completed test_action_type_field_validations")

def test_read_action_type(action_type_factory):
    logger.info("Starting test_read_action_type")
    action_type = action_type_factory(description='Bill is introduced')
    
    # Fetch the action_type from the database and check the description
    fetched_action_type = ActionType.query.get(action_type.id)
    assert fetched_action_type.description == 'Bill is introduced'
    logger.info("Completed test_read_action_type")


def test_update_action_type(session, action_type_factory):
    logger.info("Starting test_update_action_type")
    action_type = action_type_factory(description='Bill is introduced')
    
    # Update the description of the action_type
    action_type.description = 'Bill is reintroduced'
    session.commit()
    
    # Fetch the updated action_type from the database and check the new description
    updated_action_type = session.query(ActionType).get(action_type.id)
    assert updated_action_type.description == 'Bill is reintroduced'
    logger.info("Completed test_update_action_type")


def test_delete_action_type(session, action_type_factory, action_factory, bill_factory):
    logger.info("Starting test_delete_action_type")
    action_type = action_type_factory(description='Bill is introduced')
    action = action_factory(action_type=action_type)
    bill = bill_factory(action_type=action_type)
    
    # Update Actions associated with ActionType
    actions = session.query(Action).filter_by(action_type_id=action_type.id).all()
    for action in actions:
        action.action_type_id = None
    session.commit()

    # Update Bills associated with ActionType
    bills = session.query(Bill).filter_by(action_type_id=action_type.id).all()
    for bill in bills:
        bill.action_type_id = None
    session.commit()

    # Delete ActionType
    session.query(ActionType).filter_by(id=action_type.id).delete()
    session.commit()

    # Assert ActionType is deleted
    deleted_action_type = session.query(ActionType).filter_by(id=action_type.id).first()
    assert deleted_action_type is None
    logger.info("Completed test_delete_action_type")