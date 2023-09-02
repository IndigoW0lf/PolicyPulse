import pytest
from datetime import date
from policyapp import create_app, db
from policyapp.models import Politician, Bill, CoSponsor

@pytest.fixture(scope='module')
def new_politician():
    politician = Politician(name="Test Politician", state="Test State", party="Test Party", role="Test Role")
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
    co_sponsor = CoSponsor()
    co_sponsor.bill = bill
    co_sponsor.politician = politician
    db.session.add_all([politician, bill, co_sponsor])
    db.session.commit()

    return politician

def test_politician_creation(new_politician):
    assert new_politician is not None

def test_politician_fields(new_politician):
    assert new_politician.name == "Test Politician"
    assert new_politician.state == "Test State"
    assert new_politician.party == "Test Party"
    assert new_politician.role == "Test Role"

def test_politician_relationship(new_politician):
    assert new_politician.co_sponsored_bills[0].bill.title == "Test Bill"