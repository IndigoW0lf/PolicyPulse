import pytest
from backend.database.models.loc_summary import LOCSummary
from backend.tests.factories.loc_summary_factory import LOCSummaryFactory
from backend.tests.factories.bill_factory import BillFactory
from backend import db

@pytest.fixture
def bill(session):
    bill = BillFactory(title="Test Bill")
    session.add(bill)
    session.commit()
    return bill

@pytest.fixture
def loc_summary(session, bill):
    loc_summary = LOCSummaryFactory(bill_id=bill.id, version_code="Introduced", chamber="House", action_description="Introduced in House", summary_text="This is a test summary")
    session.add(loc_summary)
    session.commit()
    return loc_summary

@pytest.fixture
def setup_locsummary(loc_summary, bill):
    return loc_summary, bill

def test_locsummary_fields(setup_locsummary):
    loc_summary, bill = setup_locsummary
    assert loc_summary is not None
    assert loc_summary.version_code == "Introduced"
    assert loc_summary.chamber == "House"
    assert loc_summary.action_description == "Introduced in House"
    assert loc_summary.summary_text == "This is a test summary"
    assert loc_summary.bill_id == bill.id

@pytest.fixture
def session(db_session):
    yield db_session
    db_session.rollback()