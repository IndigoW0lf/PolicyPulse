import pytest
from datetime import date
from policyapp.models import Action, Bill, ActionType

def test_action_creation(init_database):
    session = init_database.session
    action = session.get(Action, 1)  
    assert action is not None

def test_field_validations(init_database):
    session = init_database.session
    action = session.get(Action, 1)  
    assert action.action_date is not None
    assert action.chamber in ["House", "Senate", None]

def test_foreign_keys(init_database):
    session = init_database.session
    action = session.get(Action, 1) 
    assert action.bill_id is not None
    assert action.action_type_id is not None

def test_relationships(init_database):
    session = init_database.session
    action = session.get(Action, 1) 
    action_type = session.query(ActionType).get(action.action_type_id) 
    bill = session.query(Bill).get(action.bill_id)

    assert action.bill.title == bill.title
    assert action_type.description == "Bill is introduced"
