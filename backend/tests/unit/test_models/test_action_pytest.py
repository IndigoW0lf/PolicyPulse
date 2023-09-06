import pytest
from datetime import date
from backend.database.models import Action, Bill, ActionType
from .conftest import create_action, create_action_type, create_bill

def test_action_creation(session):
    action_type = create_action_type(session, description="Bill is introduced")
    bill = create_bill(session, title="Test Bill", action_type_id=action_type.id)
    action = create_action(session, bill_id=bill.id, action_type_id=action_type.id)
    
    assert action is not None

def test_field_validations(session):
    action_type = create_action_type(session, description="Bill is introduced")
    bill = create_bill(session, title="Test Bill", action_type_id=action_type.id)
    action = create_action(session, bill_id=bill.id, action_type_id=action_type.id, chamber="House")
    
    assert action.action_date is not None
    assert action.chamber in ["House", "Senate", None]

def test_foreign_keys(session):
    action_type = create_action_type(session, description="Bill is introduced")
    bill = create_bill(session, title="Test Bill", action_type_id=action_type.id)
    action = create_action(session, bill_id=bill.id, action_type_id=action_type.id)
    
    assert action.bill_id is not None
    assert action.action_type_id is not None

def test_relationships(session):
    action_type = create_action_type(session, description="Bill is introduced")
    bill = create_bill(session, title="Test Bill", action_type_id=action_type.id)
    action = create_action(session, bill_id=bill.id, action_type_id=action_type.id)
    
    assert action.bill.title == bill.title
    assert action.action_type.description == "Bill is introduced"
