import pytest
from policyapp.models.action_type import ActionType

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

@pytest.mark.xfail(reason="Known issue with foreign key constraint")
def test_delete_action_type(init_database):
    session = init_database.session
    session.query(ActionType).filter_by(id=1).delete()
    session.commit()
    action_type = session.get(ActionType, 1) 
    assert action_type is None
