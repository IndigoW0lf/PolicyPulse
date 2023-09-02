import pytest
from datetime import date
from policyapp import create_app, db
from policyapp.models import Action, Bill, ActionType

@pytest.fixture(scope='function')
def new_action(init_database, session):
    action_type = session.query(ActionType).first()
    bill = session.query(Bill).first()

    if action_type is None or bill is None:
        pytest.fail("action_type or bill is None, which is unexpected")

    action = Action(action_date=date.today(), bill_id=bill.id, action_type_id=action_type.id)
    session.add(action)
    session.commit()

    yield action

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
    assert new_action.action_type.description == "Bill is introduced"