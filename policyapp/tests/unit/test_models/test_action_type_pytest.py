import pytest
from policyapp import create_app, db
from policyapp.models.action_type import ActionType

@pytest.fixture
def test_client():
    app = create_app(config_name='testing')
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()

@pytest.fixture
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert user data
    action_type1 = ActionType(id=1, description='Bill is introduced')
    action_type2 = ActionType(id=2, description='Bill is passed')

    db.session.add(action_type1)
    db.session.add(action_type2)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()

def test_create_action_type(test_client, init_database):
    new_action_type = ActionType(id=3, description='Bill is failed')
    init_database.session.add(new_action_type)
    init_database.session.commit()
    action_type = ActionType.query.get(3)
    assert action_type.description == 'Bill is failed'

def test_read_action_type(test_client, init_database):
    action_type = ActionType.query.get(1)
    assert action_type.description == 'Bill is introduced'

def test_update_action_type(test_client, init_database):
    action_type = ActionType.query.get(1)
    action_type.description = 'Bill is reintroduced'
    init_database.session.commit()
    updated_action_type = ActionType.query.get(1)
    assert updated_action_type.description == 'Bill is reintroduced'

def test_delete_action_type(test_client, init_database):
    ActionType.query.filter_by(id=1).delete()
    init_database.session.commit()
    action_type = ActionType.query.get(1)
    assert action_type is None
