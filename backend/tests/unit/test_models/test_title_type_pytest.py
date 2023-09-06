import pytest
from backend.database.models import TitleType
from .conftest import create_title_type, create_bill

def test_title_type_creation(session):
    title_type = create_title_type(session)
    assert title_type is not None

def test_title_type_fields(session):
    title_type = create_title_type(session, code="HR", description="House Resolution")
    assert title_type.code == "HR"
    assert title_type.description == "House Resolution"

def test_title_type_relationship(session):
    title_type = create_title_type(session)
    bill = create_bill(session, title_type_id=title_type.id)
    assert title_type.bills[0].title == bill.title
