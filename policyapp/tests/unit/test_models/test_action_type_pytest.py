import pytest
from policyapp.models.action_type import ActionType
from policyapp.models.action import Action
from policyapp.models.bill import Bill

def test_create_action_type(init_database):
    session = init_database.session
    new_action_type = ActionType(id=3, description='Bill is failed')
    session.add(new_action_type)
    session.commit()
    action_type = session.get(ActionType, 3) 
    assert action_type.description == 'Bill is failed'

def test_read_action_type(init_database):
    session = init_database.session
    action_type = session.get(ActionType, 1)  
    assert action_type.description == 'Bill is introduced'

def test_update_action_type(init_database):
    session = init_database.session
    action_type = session.get(ActionType, 1)  
    action_type.description = 'Bill is reintroduced'
    session.commit()
    updated_action_type = session.get(ActionType, 1)  
    assert updated_action_type.description == 'Bill is reintroduced'

def test_delete_action_type(init_database):
    session = init_database.session

    # Update Actions associated with ActionType id=1
    actions = session.query(Action).filter_by(action_type_id=1).all()
    for action in actions:
        action.action_type_id = None
    session.commit()

    # Update Bills associated with ActionType id=1
    bills = session.query(Bill).filter_by(action_type_id=1).all()
    for bill in bills:
        bill.action_type_id = None
    session.commit()

    # Delete ActionType
    session.query(ActionType).filter_by(id=1).delete()
    session.commit()

    # Assert ActionType is deleted
    action_type = session.query(ActionType).filter_by(id=1).first()
    assert action_type is None