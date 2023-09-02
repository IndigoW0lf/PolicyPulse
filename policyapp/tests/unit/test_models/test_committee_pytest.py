import pytest
from datetime import date
from policyapp import create_app, db
from policyapp.models import Committee, Bill

@pytest.fixture(scope='module')
def new_committee():
    committee = Committee(name="Test Committee", chamber="House", committee_code="TC001")
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
    committee.bills.append(bill)
    db.session.add_all([committee, bill])
    db.session.commit()

    return committee

def test_committee_creation(new_committee):
    assert new_committee is not None

def test_committee_fields(new_committee):
    assert new_committee.name == "Test Committee"
    assert new_committee.chamber == "House"
    assert new_committee.committee_code == "TC001"

def test_committee_relationship(new_committee):
    assert new_committee.bills[0].title == "Test Bill"