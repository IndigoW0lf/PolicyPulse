import pytest
from datetime import date
from policyapp import create_app, db
from policyapp.models import Amendment, Bill

@pytest.fixture(scope='module')
def new_amendment():
    bill = Bill(title="Test Bill")
    db.session.add(bill)
    db.session.commit()

    amendment = Amendment(
        amendment_number="A001",
        description="Test Amendment",
        date_proposed=date.today(),
        status="Proposed",
        bill_id=bill.id
    )
    db.session.add(amendment)
    db.session.commit()

    return amendment

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('testing')

    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

def test_amendment_creation(new_amendment):
    assert new_amendment is not None

def test_field_validations(new_amendment):
    assert new_amendment.amendment_number == "A001"
    assert new_amendment.description == "Test Amendment"
    assert new_amendment.date_proposed == date.today()
    assert new_amendment.status == "Proposed"

def test_foreign_keys(new_amendment):
    assert new_amendment.bill_id is not None

def test_relationships(new_amendment):
    assert new_amendment.bill.title == "Test Bill"
