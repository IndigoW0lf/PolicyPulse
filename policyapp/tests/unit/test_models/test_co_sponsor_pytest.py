import pytest
from datetime import date
from policyapp import create_app, db
from policyapp.models import CoSponsor, Bill, Politician

@pytest.fixture(scope='module')
def new_cosponsor():
    politician = Politician(name="Test Politician")
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
    db.session.add_all([politician, bill])
    db.session.commit()

    cosponsor = CoSponsor(bill_id=bill.id, politician_id=politician.id)
    db.session.add(cosponsor)
    db.session.commit()

    return cosponsor

def test_cosponsor_creation(new_cosponsor):
    assert new_cosponsor is not None

def test_cosponsor_fields(new_cosponsor):
    assert new_cosponsor.bill_id is not None
    assert new_cosponsor.politician_id is not None
