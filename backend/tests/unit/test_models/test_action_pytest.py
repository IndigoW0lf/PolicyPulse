import pytest
from backend.database.models import Action, Bill, ActionType
from backend.tests.factories.action_type_factory import ActionTypeFactory 
from backend.tests.factories.action_factory import ActionFactory
from backend.tests.factories.bill_factory import BillFactory
from backend.tests.factories.politician_factory import PoliticianFactory
from backend.tests.factories.title_type_factory import TitleTypeFactory

@pytest.fixture
def action_type(session):
    action_type = ActionTypeFactory()
    session.add(action_type)
    session.commit()
    return action_type

@pytest.fixture
def politician(session):
    politician = PoliticianFactory()
    session.add(politician)
    session.commit()
    return politician

@pytest.fixture
def title_type(session):
    title_type = TitleTypeFactory()
    session.add(title_type)
    session.commit()
    return title_type

@pytest.fixture
def bill(session, politician, title_type):
    bill = BillFactory(sponsor_id=politician.id, title_type_id=title_type.id)
    session.add(bill)
    session.commit()
    return bill

@pytest.fixture
def action(session, action_type, bill):
    action = ActionFactory(action_type_id=action_type.id, bill_id=bill.id)
    session.add(action)
    session.commit()
    return action

def test_action_relationship(session, action_type):
    # Step 3: Use the ID of the created ActionType record
    action = ActionFactory(action_type_id=action_type.id)
    session.add(action)
    session.commit()

    # Adding an assertion to check if the action has been created successfully
    assert action.id is not None

@pytest.fixture
def setup_actions(action, bill, action_type):
    return action, bill, action_type

def test_action_creation(setup_actions):
    action, _, _ = setup_actions
    assert action is not None

def test_field_validations(setup_actions):
    action, _, _ = setup_actions
    assert action.action_date is not None
    assert action.chamber in ["House", "Senate", None]

def test_foreign_keys(setup_actions):
    action, bill, action_type = setup_actions
    assert action.bill_id == bill.id
    assert action.action_type_id == action_type.id

def test_relationships(setup_actions):
    action, bill, action_type = setup_actions
    assert action.bill.title == bill.title
    assert action.action_type.description == action_type.description

@pytest.fixture
def session(db_session):
    yield db_session
    db_session.rollback()
