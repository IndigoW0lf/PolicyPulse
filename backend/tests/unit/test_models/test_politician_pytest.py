import pytest
from datetime import date
from backend.database.models import Politician, CoSponsor

def test_politician_creation(init_database):
    session = init_database.session
    politician = session.get(Politician, 1)
    assert politician is not None

def test_politician_fields(init_database):
    session = init_database.session
    politician = session.get(Politician, 1)  
    assert politician.name == "Test Politician"
    assert politician.state == "Test State"
    assert politician.party == "Test Party"
    assert politician.role == "Test Role"
    assert politician.profile_link == "http://example.com/profile"

def test_politician_sponsored_bills_relationship(init_database):
    session = init_database.session
    politician = session.get(Politician, 1)
    assert politician.sponsored_bills[0].title == "Test Bill"

def test_politician_co_sponsored_bills_relationship(init_database):
    session = init_database.session
    politician = session.get(Politician, 1)
    co_sponsored_bill = session.query(CoSponsor).filter_by(politician_id=politician.id).first().bill
    assert co_sponsored_bill.title == "Test Bill"
