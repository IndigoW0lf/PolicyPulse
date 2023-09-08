import pytest
import logging
from sqlalchemy.exc import IntegrityError
from backend.tests.factories.subject_factory import SubjectFactory
from backend.tests.factories.bill_factory import BillFactory
from backend.database.models import Subject, Bill

logger = logging.getLogger(__name__)

@pytest.fixture
def subject_factory(session):
    def _subject_factory(**kwargs):
        subject = SubjectFactory(**kwargs)
        session.add(subject)
        session.commit()
        return subject
    return _subject_factory

@pytest.fixture
def bill_factory(session):
    def _bill_factory(**kwargs):
        bill = BillFactory(**kwargs)
        session.add(bill)
        session.commit()
        return bill
    return _bill_factory

def test_subject_creation(subject_factory):
    logger.info("Starting test_subject_creation")
    subject = subject_factory(name="Test Subject 1", description="This is a test subject 1.")

    assert subject is not None
    assert subject.id is not None
    assert subject.name == "Test Subject 1"
    assert subject.description == "This is a test subject 1."

    # Fetch the subject from the database and check the fields
    fetched_subject = Subject.query.get(subject.id)
    assert fetched_subject.name == subject.name
    assert fetched_subject.description == subject.description
    logger.info("Completed test_subject_creation")

def test_subject_field_validations(session, subject_factory):
    logger.info("Starting test_subject_field_validations")
    # Test that subject cannot be created with a null name
    with pytest.raises(IntegrityError):
        subject = subject_factory(name=None)
        session.add(subject)
        session.commit()

    session.rollback()
    logger.info("Completed test_subject_field_validations")

def test_subject_relationships(session, subject_factory, bill_factory):
    logger.info("Starting test_subject_relationships")
    subject = subject_factory(name="Test Subject 1", description="This is a test subject 1.")
    bill = bill_factory(bill_number="HR002", title="Related Test Bill")
    subject.bills.append(bill)
    session.add(subject)
    session.add(bill)
    session.commit()
    
    assert subject.bills[0].title == bill.title
    logger.info("Completed test_subject_relationships")
