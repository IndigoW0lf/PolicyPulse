import pytest
from policyapp import create_app, db
from policyapp.models.action_type import ActionType

@pytest.fixture
def test_client():
    print("Setting up test client")
    app = create_app(config_name='testing')
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield testing_client 
    ctx.pop()

def test_create_action_type(init_database):
    new_action_type = ActionType(id=3, description='Bill is failed')
    init_database.session.add(new_action_type)
    init_database.session.commit()
    action_type = init_database.session.get(ActionType, 3)
    assert action_type.description == 'Bill is failed'

def test_read_action_type(init_database):
    action_type = init_database.session.get(ActionType, 1)
    assert action_type.description == 'Bill is introduced'

def test_update_action_type(init_database):
    action_type = init_database.session.get(ActionType, 1)
    action_type.description = 'Bill is reintroduced'
    init_database.session.commit()
    updated_action_type = init_database.session.get(ActionType, 1)
    assert updated_action_type.description == 'Bill is reintroduced'

@pytest.mark.xfail(reason="Known issue with foreign key constraint")
def test_delete_action_type(init_database):
    init_database.session.query(ActionType).filter_by(id=1).delete()
    init_database.session.commit()
    action_type = init_database.session.get(ActionType, 1)
    assert action_type is None
