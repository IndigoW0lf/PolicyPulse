import pytest
from policyapp.models import Committee

def test_committee_creation(init_database):
    session = init_database.session
    committee = session.query(Committee).first()
    assert committee is not None

def test_committee_fields(init_database):
    session = init_database.session
    committee = session.query(Committee).first()
    assert committee.name == "Test Committee"
    assert committee.chamber == "House"
    assert committee.committee_code == "TC001"

def test_committee_relationship(init_database):
    session = init_database.session
    committee = session.query(Committee).first()
    
    # Debugging output
    print("Committee:", committee)
    print("Related Bills:", committee.bills)
    
    if committee.bills:
        assert committee.bills[0].title == "Test Bill"
    else:
        assert False, "committee.bills is empty"

