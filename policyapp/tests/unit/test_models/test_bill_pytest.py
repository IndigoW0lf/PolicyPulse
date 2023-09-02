import pytest
from datetime import date
from policyapp import create_app, db
from policyapp.models import Bill, Politician

@pytest.fixture(scope='module')
def new_bill():
    politician = Politician(name="Test Politician")
    db.session.add(politician)
    db.session.commit()

    bill = Bill(
        title="Test Bill",
        summary="This is a test bill",
        date_introduced=date.today(),
        status="Proposed",
        bill_number="HR001",
        sponsor_name="Test Politician",
    )
    db.session.add(bill)
    db.session.commit()

    return bill

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('testing')

    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

def test_bill_creation(new_bill):
    assert new_bill is not None

def test_field_validations(new_bill):
    assert new_bill.title == "Test Bill"
    assert new_bill.summary == "This is a test bill"
    assert new_bill.date_introduced == date.today()
    assert new_bill.status == "Proposed"
    assert new_bill.bill_number == "HR001"
    assert new_bill.sponsor_name == "Test Politician"

def test_foreign_keys(new_bill):
    assert new_bill.sponsor_name is not None

def test_relationships(new_bill):
    assert new_bill.sponsor.name == "Test Politician"
