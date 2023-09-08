import pytest
from datetime import date
from backend.database.models import Amendment, Bill, AmendmentStatusEnum
from backend.tests.factories.amendment_factory import AmendmentFactory
from backend.tests.factories.bill_factory import BillFactory

@pytest.fixture
def bill(session):
    bill = BillFactory()
    session.add(bill)
    session.commit()
    return bill

@pytest.fixture
def amendment(session, bill):
    amendment = AmendmentFactory(bill_id=bill.id, amendment_number="A001", description="Test Amendment", date_proposed=date.today(), status=AmendmentStatusEnum.PROPOSED)
    session.add(amendment)
    session.commit()
    return amendment

@pytest.fixture
def setup_amendment(amendment, bill):
    return amendment, bill

def test_create_amendment(setup_amendment):
    amendment, _ = setup_amendment
    assert amendment is not None

def test_field_validations(setup_amendment):
    amendment, _ = setup_amendment
    assert amendment.amendment_number == "A001"
    assert amendment.description == "Test Amendment"
    assert amendment.date_proposed == date.today()
    assert amendment.status == AmendmentStatusEnum.PROPOSED

def test_foreign_keys(setup_amendment):
    amendment, _ = setup_amendment
    assert amendment.bill_id is not None

def test_relationships(setup_amendment):
    amendment, bill = setup_amendment
    assert amendment.bill.title == bill.title
