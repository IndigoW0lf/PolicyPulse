import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.database.models import Committee, Bill
from backend.tests.factories.committee_factory import CommitteeFactory
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
def committee_factory(session):
    def _committee_factory(**kwargs):
        committee = CommitteeFactory(**kwargs)
        session.add(committee)
        session.commit()
        return committee
    return _committee_factory

def test_committee_creation(committee_factory):
    logger.info("Starting test_committee_creation")
    committee = committee_factory(name="Test Committee", chamber="House", committee_code="TC001")

    assert committee is not None
    assert committee.id is not None
    assert committee.name == "Test Committee"
    assert committee.chamber == "House"
    assert committee.committee_code == "TC001"

    # Fetch the committee from the database and check the fields
    fetched_committee = Committee.query.get(committee.id)
    assert fetched_committee.name == committee.name
    assert fetched_committee.chamber == committee.chamber
    assert fetched_committee.committee_code == committee.committee_code
    logger.info("Completed test_committee_creation")

def test_committee_field_validations(session, committee_factory):
    logger.info("Starting test_committee_field_validations")
    # Test that committee cannot be created with null fields (if necessary)
    with pytest.raises(IntegrityError):
        committee = committee_factory(name=None)
        session.add(committee)
        session.commit()

    session.rollback()
    logger.info("Completed test_committee_field_validations")

def test_committee_relationships(committee_factory, bill_factory, session):
    logger.info("Starting test_committee_relationships")
    bill = bill_factory(title="Test Bill")
    committee = committee_factory(name="Test Committee", chamber="House", committee_code="TC001")

    committee.bills.append(bill)
    session.flush()

    assert committee.bills[0].title == bill.title
    logger.info("Completed test_committee_relationships")