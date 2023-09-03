import pytest
from datetime import date
from policyapp.models import TitleType

def test_title_type_creation(init_database):
    session = init_database.session
    title_type = session.query(TitleType).first()
    assert title_type is not None

def test_title_type_fields(init_database):
    session = init_database.session
    title_type = session.query(TitleType).first()
    
    assert title_type.code == "HR"
    assert title_type.description == "House Resolution"

def test_title_type_relationship(init_database):
    session = init_database.session
    title_type = session.query(TitleType).first()
    
    assert title_type.bills[0].title == "Test Bill"