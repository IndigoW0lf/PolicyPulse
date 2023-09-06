import pytest
from backend.database.models import Politician, CoSponsor
from .conftest import create_politician, create_bill, create_cosponsor

def test_politician_creation(session):
    politician = create_politician(session)
    assert politician is not None

def test_politician_fields(session):
    politician = create_politician(session, name="Test Politician", state="Test State", party="Test Party", role="Test Role", profile_link="http://example.com/profile")
    assert politician.name == "Test Politician"
    assert politician.state == "Test State"
    assert politician.party == "Test Party"
    assert politician.role == "Test Role"
    assert politician.profile_link == "http://example.com/profile"

def test_politician_sponsored_bills_relationship(session):
    politician = create_politician(session)
    bill = create_bill(session, sponsor_id=politician.id)
    assert politician.sponsored_bills[0].title == bill.title

def test_politician_co_sponsored_bills_relationship(session):
    politician = create_politician(session)
    bill = create_bill(session)
    cosponsor = create_cosponsor(session, bill_id=bill.id, politician_id=politician.id)
    assert cosponsor.bill.title == bill.title
