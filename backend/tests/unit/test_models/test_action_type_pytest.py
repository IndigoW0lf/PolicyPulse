import pytest
from backend.database.models import Action, Bill, ActionType
from backend.tests.factories.action_type_factory import ActionTypeFactory 
from backend.tests.factories.action_factory import ActionFactory
from backend.tests.factories.bill_factory import BillFactory

@pytest.fixture
def action_type(session):
    action_type = ActionTypeFactory(description='Bill is introduced')
    session.add(action_type)
    session.commit()
    return action_type

@pytest.fixture
def bill(session, action_type):
    bill = BillFactory(action_type_id=action_type.id)
    session.add(bill)
    session.commit()
    return bill

@pytest.fixture
def action(session, action_type, bill):
    action = ActionFactory(action_type_id=action_type.id, bill_id=bill.id)
    session.add(action)
    session.commit()
    return action

@pytest.fixture
def setup_action_type(action_type, action, bill):
    return action_type, action, bill

def test_create_action_type(setup_action_type):
    action_type, _, _ = setup_action_type
    assert action_type is not None

def test_read_action_type(setup_action_type):
    action_type, _, _ = setup_action_type
    assert action_type.description == 'Bill is introduced'

def test_update_action_type(setup_action_type, session):
    action_type, _, _ = setup_action_type
    action_type.description = 'Bill is reintroduced'
    session.commit()
    updated_action_type = session.get(ActionType, action_type.id)  
    assert updated_action_type.description == 'Bill is reintroduced'

def test_delete_action_type(setup_action_type, session):
    action_type, action, bill = setup_action_type
    
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

@pytest.fixture
def session(db_session):
    yield db_session
    db_session.rollback()
