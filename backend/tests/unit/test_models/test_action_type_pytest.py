import pytest
from backend.database.models.action_type import ActionType
from backend.database.models.action import Action
from backend.database.models.bill import Bill
from .conftest import create_action_type, create_action, create_bill

def test_create_action_type(session):
    new_action_type = create_action_type(session, description='Bill is failed')
    assert new_action_type.description == 'Bill is failed'

def test_read_action_type(session):
    action_type = create_action_type(session, description='Bill is introduced')
    assert action_type.description == 'Bill is introduced'

def test_update_action_type(session):
    action_type = create_action_type(session, description='Bill is introduced')
    action_type.description = 'Bill is reintroduced'
    session.commit()
    updated_action_type = session.get(ActionType, action_type.id)  
    assert updated_action_type.description == 'Bill is reintroduced'

def test_delete_action_type(session):
    action_type = create_action_type(session, description='Bill is introduced')
    
    # Create associated actions and bills
    bill = create_bill(session, action_type_id=action_type.id)
    create_action(session, action_type_id=action_type.id, bill_id=bill.id)

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
