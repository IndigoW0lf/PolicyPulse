import pytest
from policyapp import create_app, db
from policyapp.models import TitleType, Bill

@pytest.fixture(scope='module')
def new_title_type():
    title_type = TitleType(code="HR", description="House Resolution")
    bill = Bill(title="Test Bill", bill_number="HR001", sponsor_name="Test Politician", title_type_id=title_type.id)
    db.session.add_all([title_type, bill])
    db.session.commit()

    return title_type

def test_title_type_creation(new_title_type):
    assert new_title_type is not None

def test_title_type_fields(new_title_type):
    assert new_title_type.code == "HR"
    assert new_title_type.description == "House Resolution"

def test_title_type_relationship(new_title_type):
    assert new_title_type.bills[0].title == "Test Bill"

