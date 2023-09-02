import pytest
from datetime import date
from policyapp import create_app, db
from policyapp.models import TitleType, Bill

@pytest.fixture(scope='module')
def new_title_type():
    title_type = TitleType(code="HR", description="House Resolution")
    bill = Bill(
        title="Test Bill",
        summary="This is a test summary",
        date_introduced=date.today(),
        status="Proposed",
        bill_number="HR001",
        sponsor_name="Test Sponsor",
        committee="Test Committee",
        voting_record="Yea: 10, Nay: 5",
        full_text_link="http://example.com/full_text",
        tags="Test, Bill",
        last_action_date=date.today(),
        last_action_description="Introduced in House",
        congress="117th",
        bill_type="House Bill",
        sponsor_id=1
    )
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

