import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.database.models import LOCSummary, Bill
from backend.tests.factories.loc_summary_factory import LOCSummaryFactory
from backend.tests.factories.bill_factory import BillFactory

logger = logging.getLogger(__name__)

@pytest.fixture
def bill_factory(session):
    def _bill_factory(**kwargs):
        bill = BillFactory(**kwargs)
        session.add(bill)
        session.commit()
        return bill
    return _bill_factory

@pytest.fixture
def loc_summary_factory(session):
    def _loc_summary_factory(**kwargs):
        loc_summary = LOCSummaryFactory(**kwargs)
        session.add(loc_summary)
        session.commit()
        return loc_summary
    return _loc_summary_factory

def test_loc_summary_creation(loc_summary_factory, bill_factory):
    logger.info("Starting test_loc_summary_creation")
    bill = bill_factory(title="Test Bill")
    loc_summary = loc_summary_factory(bill=bill, version_code="Introduced", chamber="House", action_description="Introduced in House", summary_text="This is a test summary")

    assert loc_summary is not None
    assert loc_summary.id is not None
    assert loc_summary.version_code == "Introduced"
    assert loc_summary.chamber == "House"
    assert loc_summary.action_description == "Introduced in House"
    assert loc_summary.summary_text == "This is a test summary"

    # Fetch the loc_summary from the database and check the fields
    fetched_loc_summary = LOCSummary.query.get(loc_summary.id)
    assert fetched_loc_summary.version_code == loc_summary.version_code
    assert fetched_loc_summary.chamber == loc_summary.chamber
    assert fetched_loc_summary.action_description == loc_summary.action_description
    assert fetched_loc_summary.summary_text == loc_summary.summary_text
    assert fetched_loc_summary.bill.title == bill.title
    logger.info("Completed test_loc_summary_creation")

def test_loc_summary_field_validations(session, loc_summary_factory):
    logger.info("Starting test_loc_summary_field_validations")
    # Test that loc_summary cannot be created with null fields (if necessary)
    with pytest.raises(IntegrityError):
        loc_summary = loc_summary_factory(version_code=None)
        session.add(loc_summary)
        session.commit()

    session.rollback()
    logger.info("Completed test_loc_summary_field_validations")

def test_loc_summary_relationships(loc_summary_factory, bill_factory):
    logger.info("Starting test_loc_summary_relationships")
    bill = bill_factory(title="Test Bill")
    loc_summary = loc_summary_factory(bill=bill, version_code="Introduced")

    assert loc_summary.bill == bill
    logger.info("Completed test_loc_summary_relationships")