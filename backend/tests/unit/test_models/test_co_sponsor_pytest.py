import pytest
from backend.database.models import CoSponsor
from .conftest import create_cosponsor, create_bill, create_politician

def test_cosponsor_creation(session):
    cosponsor = create_cosponsor(session)
    assert cosponsor is not None

def test_cosponsor_fields(session):
    bill = create_bill(session)
    politician = create_politician(session)
    cosponsor = create_cosponsor(session, bill_id=bill.id, politician_id=politician.id)
    assert cosponsor.bill_id == bill.id
    assert cosponsor.politician_id == politician.id
