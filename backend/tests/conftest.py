import pytest
import logging
from backend.tests.factories.action_factory import ActionFactory
from backend.tests.factories.action_type_factory import ActionTypeFactory
from backend.tests.factories.amendment_factory import AmendmentFactory
from backend.tests.factories.bill_full_text_factory import BillFullTextFactory
from backend.tests.factories.committee_factory import CommitteeFactory
from backend.tests.factories.co_sponsor_factory import CoSponsorFactory
from backend.tests.factories.loc_summary_factory import LOCSummaryFactory
from backend.tests.factories.related_bill_factory import RelatedBillFactory
from backend.tests.factories.subject_factory import SubjectFactory
from backend.tests.factories.title_type_factory import TitleTypeFactory
from backend.tests.factories.politician_factory import PoliticianFactory
from backend.tests.factories.bill_factory import BillFactory
from backend import create_app, db

logger = logging.getLogger(__name__)

def create_fixture(session, factory_class):
    try:
        instance = factory_class()
        session.add(instance)
        session.commit()
        logger.info(f"{factory_class.__name__} fixture created successfully")
        return instance
    except Exception as e:
        logger.error(f"Error creating {factory_class.__name__} fixture: {e}")
        raise

@pytest.fixture(scope='function')
def session():
    app = create_app('testing')
    with app.app_context():
        db.drop_all()  # Drop all tables to ensure a clean state
        db.create_all()  # Create all tables
        try:
            yield db.session  # Provide the session to the test
        except Exception as e:
            logger.error(f"Error during session: {e}")
            raise
        finally:
            db.session.rollback()  # Roll back any changes
            db.drop_all()  # Drop all tables to clean up
            logger.info("Session rolled back and tables dropped successfully")

@pytest.fixture
def action_factory(session):
    return lambda: create_fixture(session, ActionFactory)

@pytest.fixture
def action_type_factory(session):
    return lambda: create_fixture(session, ActionTypeFactory)

@pytest.fixture
def amendment_factory(session):
    return lambda: create_fixture(session, AmendmentFactory)

@pytest.fixture
def bill_factory(session):
    return lambda: create_fixture(session, BillFactory)

@pytest.fixture
def bill_full_text_factory(session):
    return lambda: create_fixture(session, BillFullTextFactory)

@pytest.fixture
def committee_factory(session):
    return lambda: create_fixture(session, CommitteeFactory)

@pytest.fixture
def co_sponsor_factory(session):
    return lambda: create_fixture(session, CoSponsorFactory)

@pytest.fixture
def loc_summary_factory(session):
    return lambda: create_fixture(session, LOCSummaryFactory)

@pytest.fixture
def politician_factory(session):
    return lambda: create_fixture(session, PoliticianFactory)

@pytest.fixture
def related_bill_factory(session):
    return lambda: create_fixture(session, RelatedBillFactory)

@pytest.fixture
def subject_factory(session):
    return lambda: create_fixture(session, SubjectFactory)

@pytest.fixture
def title_type_factory(session):
    return lambda: create_fixture(session, TitleTypeFactory)