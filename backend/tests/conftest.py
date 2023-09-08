import pytest
import logging
from .factories.action_factory import ActionFactory
from .factories.action_type_factory import ActionTypeFactory
from .factories.amendment_factory import AmendmentFactory
from .factories.bill_full_text_factory import BillFullTextFactory
from .factories.committee_factory import CommitteeFactory
from .factories.co_sponsor_factory import CoSponsorFactory
from .factories.loc_summary_factory import LOCSummaryFactory
from .factories.related_bill_factory import RelatedBillFactory
from .factories.subject_factory import SubjectFactory
from .factories.title_type_factory import TitleTypeFactory
from .factories.politician_factory import PoliticianFactory
from .factories.bill_factory import BillFactory
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

@pytest.fixture
def action(session):
    return create_fixture(session, ActionFactory)

@pytest.fixture
def action_type(session):
    return create_fixture(session, ActionTypeFactory)

@pytest.fixture
def amendment(session):
    return create_fixture(session, AmendmentFactory)

@pytest.fixture
def bill(session):
    return create_fixture(session, BillFactory)

@pytest.fixture
def bill_full_text(session):
    return create_fixture(session, BillFullTextFactory)

@pytest.fixture
def committee(session):
    return create_fixture(session, CommitteeFactory)

@pytest.fixture
def cosponsor(session):
    return create_fixture(session, CoSponsorFactory)

@pytest.fixture
def locsummary(session):
    return create_fixture(session, LOCSummaryFactory)

@pytest.fixture
def politician(session):
    return create_fixture(session, PoliticianFactory)

@pytest.fixture
def related_bill(session):
    return create_fixture(session, RelatedBillFactory)

@pytest.fixture
def subject(session):
    return create_fixture(session, SubjectFactory)

@pytest.fixture
def title_type(session):
    return create_fixture(session, TitleTypeFactory)

@pytest.fixture(scope='session')
def session():
    try:
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            db.session.begin_nested()
            logger.info("Session started successfully")
            yield db.session
            db.session.rollback()
            logger.info("Session rolled back successfully")
    except Exception as e:
        logger.error(f"Error in session fixture: {e}")
        raise
