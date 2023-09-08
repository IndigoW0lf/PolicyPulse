import pytest
from backend.database.models.title_type import TitleType
from backend.tests.factories.title_type_factory import TitleTypeFactory
from backend.tests.factories.bill_factory import BillFactory
from backend import db

@pytest.fixture
def title_type(session):
    title_type = TitleTypeFactory(code="HR", description="House Resolution")
    session.add(title_type)
    session.commit()
    return title_type

@pytest.fixture
def bill(session, title_type):
    bill = BillFactory(title="Test Bill", title_type_id=title_type.id)
    session.add(bill)
    session.commit()
    return bill

@pytest.fixture
def setup_title_type(title_type):
    return title_type

def test_title_type_creation(setup_title_type):
    title_type = setup_title_type
    assert title_type is not None

def test_title_type_fields(setup_title_type):
    title_type = setup_title_type
    assert title_type.code == "HR"
    assert title_type.description == "House Resolution"

def test_title_type_relationship(setup_title_type, bill, session):
    title_type = setup_title_type
    assert title_type.bills[0].title == bill.title
