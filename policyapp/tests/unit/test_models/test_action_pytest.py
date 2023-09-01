import pytest
from datetime import date
from policyapp import create_app, db
from policyapp.models import Action, Bill, ActionType

@pytest.fixture(scope='module')
def new_action():
    bill = Bill(title="Test Bill")
    action_type = ActionType(name="Test Action Type")
    db.session.add_all([bill, action_type])
    db.session.commit()

    action = Action(action_date=date.today(), bill_id=bill.id, action_type_id=action_type.id)
    db.session.add(action)
    db.session.commit()

    return action

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('testing')

    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

def test_action_creation(new_action):
    assert new_action is not None

def test_field_validations(new_action):
    assert new_action.action_date is not None
    assert new_action.chamber in ["House", "Senate", None]

def test_foreign_keys(new_action):
    assert new_action.bill_id is not None
    assert new_action.action_type_id is not None

def test_relationships(new_action):
    assert new_action.bill.title == "Test Bill"
    assert new_action.action_type.name == "Test Action Type"
