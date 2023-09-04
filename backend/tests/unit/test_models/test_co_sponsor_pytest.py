import pytest
from backend.database.models import CoSponsor

# Use init_database fixture from conftest.py
def test_cosponsor_creation(init_database):
    session = init_database.session  # Access the session from the init_database fixture
    cosponsor = session.query(CoSponsor).first()
    assert cosponsor is not None

def test_cosponsor_fields(init_database):
    session = init_database.session
    cosponsor = session.query(CoSponsor).first()
    assert cosponsor.bill_id is not None
    assert cosponsor.politician_id is not None
