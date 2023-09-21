import pytest
import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from backend.tests.conftest import create_fixture
from backend.database.models import Bill, ActionType, Politician
from backend.tests.factories.bill_factory import BillFactory
from backend.tests.factories.action_type_factory import ActionTypeFactory
from backend.tests.factories.politician_factory import PoliticianFactory
from backend.tests.factories.policy_area_factory import PolicyAreaFactory
from backend.tests.factories.committee_factory import CommitteeFactory
from backend.tests.factories.subject_factory import SubjectFactory
from backend.tests.factories.bill_full_text_factory import BillFullTextFactory
from backend.tests.factories.recorded_vote_factory import RecordedVoteFactory
from backend.tests.factories.related_bill_factory import RelatedBillFactory
from backend.tests.factories.note_factory import NoteFactory
from backend.tests.factories.loc_summary_factory import LOCSummaryFactory
from backend.tests.factories.law_factory import LawFactory
from backend.tests.factories.amendment_factory import AmendmentFactory
from backend.tests.factories.amended_bill_factory import AmendedBillFactory
from backend.tests.factories.amendment_link_factory import AmendmentLinkFactory
from backend.tests.factories.co_sponsor_factory import CoSponsorFactory
from backend.tests.factories.loc_summary_code_factory import LOCSummaryCodeFactory


logger = logging.getLogger(__name__)


@pytest.fixture
def action_type_factory(session):
    def _action_type_factory(**kwargs):
        return create_fixture(session, ActionTypeFactory, **kwargs)
    return _action_type_factory

@pytest.fixture
def bill_factory(session, politician_factory, action_type_factory, policy_area_factory):
    def _bill_factory(**kwargs):
        if 'sponsor' not in kwargs:
            kwargs['sponsor'] = politician_factory()
        if 'action_type' not in kwargs:
            kwargs['action_type'] = action_type_factory()
        if 'policy_area' not in kwargs:
            kwargs['policy_area'] = policy_area_factory()

        return create_fixture(session, BillFactory, **kwargs)
    return _bill_factory

@pytest.fixture
def amendment_factory(session):
    def _amendment_factory(**kwargs):
        return create_fixture(session, AmendmentFactory, **kwargs)
    return _amendment_factory

@pytest.fixture
def committee_factory(session):
    def _committee_factory(**kwargs):
        return create_fixture(session, CommitteeFactory, **kwargs)
    return _committee_factory

@pytest.fixture
def subject_factory(session):
    def _subject_factory(**kwargs):
        return create_fixture(session, SubjectFactory, **kwargs)
    return _subject_factory

@pytest.fixture
def bill_full_text_factory(session):
    def _bill_full_text_factory(**kwargs):
        return create_fixture(session, BillFullTextFactory, **kwargs)
    return _bill_full_text_factory

@pytest.fixture
def recorded_vote_factory(session):
    def _recorded_vote_factory(**kwargs):
        return create_fixture(session, RecordedVoteFactory, **kwargs)
    return _recorded_vote_factory

@pytest.fixture
def related_bill_factory(session):
    def _related_bill_factory(**kwargs):
        return create_fixture(session, RelatedBillFactory, **kwargs)
    return _related_bill_factory

@pytest.fixture
def note_factory(session):
    def _note_factory(**kwargs):
        return create_fixture(session, NoteFactory, **kwargs)
    return _note_factory

@pytest.fixture
def law_factory(session):
    def _law_factory(**kwargs):
        return create_fixture(session, LawFactory, **kwargs)
    return _law_factory

@pytest.fixture
def loc_summary_factory(session):
    def _loc_summary_factory(**kwargs):
        return create_fixture(session, LOCSummaryFactory, **kwargs)
    return _loc_summary_factory

@pytest.fixture
def law_factory(session, bill_factory):
    def _law_factory(**kwargs):
        if 'bill' not in kwargs:
            kwargs['bill'] = bill_factory()
        return create_fixture(session, LawFactory, **kwargs)
    return _law_factory

@pytest.fixture
def policy_area_factory(session):
    def _policy_area_factory(**kwargs):
        return create_fixture(session, PolicyAreaFactory, **kwargs)
    return _policy_area_factory

@pytest.fixture
def politician_factory(session):
    def _politician_factory(**kwargs):
        return create_fixture(session, PoliticianFactory, **kwargs)
    return _politician_factory

@pytest.fixture
def recorded_vote_factory(session, bill_factory):
    def _recorded_vote_factory(**kwargs):
        if 'bill' not in kwargs:
            kwargs['bill'] = bill_factory()
        return create_fixture(session, RecordedVoteFactory, **kwargs)
    return _recorded_vote_factory


def test_bill_creation(bill_factory, politician_factory, action_type_factory, policy_area_factory):
    logger.info("Starting test_bill_creation")
    
    # Creating required dependencies
    politician = politician_factory(name="Test Politician", state="CA", party="Democrat", role="Senator", profile_link="http://example.com", bioguide_id="B123", gpo_id="G123", lis_id="L123")
    action_type = action_type_factory(description='Bill is introduced')
    policy_area = policy_area_factory(name="Test Policy Area", description="This is a test policy area")
    
    # Creating a bill with new fields
    bill = bill_factory(
        sponsor=politician, 
        action_type=action_type, 
        policy_area=policy_area,
        title="Test Bill", 
        official_title="Test Official Title",
        summary="This is a test bill", 
        status="Proposed", 
        bill_number="HR001",
        congress="117th",
        bill_type="House Bill",
        committee="Test Committee",
        voting_record="Voting Record Details",
        full_bill_link="http://example.com",
        tags="Test Tags",
        last_action_date="2021-01-01",
        last_action_description="Test Action Description",
        update_date="2021-01-01",
        xml_content={"test_key": "test_value"},
        origin_chamber="House",
    )
    
    assert bill is not None
    assert bill.id is not None
    assert bill.title == "Test Bill"
    assert bill.official_title == "Test Official Title"
    assert bill.summary == "This is a test bill"
    assert bill.status == "Proposed"
    assert bill.bill_number == "HR001"
    assert bill.congress == "117th"  # checking new field
    assert bill.bill_type == "House Bill"  # checking new field 
    assert bill.committee == "Test Committee"
    assert bill.voting_record == "Voting Record Details"
    assert bill.full_bill_link == "http://example.com"
    assert bill.tags == "Test Tags"
    assert bill.last_action_description == "Test Action Description"
    assert bill.last_action_date == datetime.strptime("2021-01-01", "%Y-%m-%d").date()
    assert bill.update_date == datetime.strptime("2021-01-01", "%Y-%m-%d").date()
    assert bill.xml_content == {"test_key": "test_value"}
    assert bill.origin_chamber == "House"
    
    # Fetch the bill from the database and check the relationships
    fetched_bill = Bill.query.get(bill.id)
    assert fetched_bill.sponsor.name == politician.name
    assert fetched_bill.action_type.description == action_type.description
    assert fetched_bill.policy_area.name == policy_area.name
    
    logger.info("Completed test_bill_creation")


def test_bill_field_validations(session, bill_factory):
    logger.info("Starting test_bill_field_validations")
    
    non_nullable_fields = [
        ('bill_number', None),
        ('date_introduced', None),
        ('full_bill_link', None),
        ('origin_chamber', None),
        ('status', None),
        ('title', None),
        ('summary', None),
        ('sponsor_id', None),
        ('created_at', None),
    ]

    nullable_fields = [
        ('committee', None),
        ('voting_record', None),
        ('tags', None),
        ('last_action_date', None),
        ('last_action_description', None),
        ('congress', None),
        ('bill_type', None),
        ('update_date', None),
        ('xml_content', None),
        ('action_type_id', None),
        ('updated_at', None),
        ('official_title', None),
    ]
    
    for field, value in non_nullable_fields:
        with pytest.raises(IntegrityError):
            bill_data = {field: value}
            bill = bill_factory(**bill_data)
            session.add(bill)
            session.commit()
        
        session.rollback()

    for field, value in nullable_fields:
        bill_data = {field: value}
        bill = bill_factory(**bill_data)
        session.add(bill)
        session.commit()
        assert getattr(bill, field) == value
        
        session.rollback()

    logger.info("Completed test_bill_field_validations")

def test_bill_foreign_keys(session, bill_factory):
    logger.info("Starting test_bill_foreign_keys")
    # Test that bill cannot be created with non-existent sponsor_id and action_type_id
    with pytest.raises(IntegrityError):
        bill = bill_factory(sponsor_id=9999, action_type_id=9999)
        session.add(bill)
        session.commit()

    session.rollback()
    logger.info("Completed test_bill_foreign_keys")

'''Test Relationships Between Bill and Other Models'''
def test_bill_relationships(bill_factory, politician_factory, action_type_factory, policy_area_factory):
    logger.info("Starting test_bill_relationships")
    
    politician = politician_factory(name="Test Politician")
    action_type = action_type_factory(description='Bill is introduced')
    policy_area = policy_area_factory(name="Test Policy Area", description="This is a test policy area")
    
    bill = bill_factory(sponsor=politician, action_type=action_type, policy_area=policy_area)
    
    assert bill.sponsor == politician
    assert bill.action_type == action_type
    assert bill.policy_area == policy_area
    
    # Fetch the bill from the database and check the relationships
    fetched_bill = Bill.query.get(bill.id)
    assert fetched_bill.sponsor.name == politician.name
    assert fetched_bill.action_type.description == action_type.description
    assert fetched_bill.policy_area.name == policy_area.name
    
    logger.info("Completed test_bill_relationships")


def test_bill_amendment_relationship(bill_factory, amendment_factory):
    logger.info("Starting test_bill_amendment_relationship")
    
    amendment = amendment_factory(description="Test Amendment")
    bill = bill_factory(amendments=[amendment])
    
    assert bill.amendments == [amendment]
    
    # Fetch the bill from the database and check the relationship
    fetched_bill = Bill.query.get(bill.id)
    assert fetched_bill.amendments[0].description == amendment.description
    
    logger.info("Completed test_bill_amendment_relationship")


def test_bill_committee_relationship(bill_factory, committee_factory):
    logger.info("Starting test_bill_committee_relationship")
    
    committee = committee_factory(name="Test Committee")
    bill = bill_factory(committees=[committee])
    
    assert bill.committees == [committee]
    
    # Fetch the bill from the database and check the relationship
    fetched_bill = Bill.query.get(bill.id)
    assert fetched_bill.committees[0].name == committee.name
    
    logger.info("Completed test_bill_committee_relationship")


def test_bill_policy_area_relationship(bill_factory, policy_area_factory):
    logger.info("Starting test_bill_policy_area_relationship")
    
    policy_area = policy_area_factory(name="Test Policy Area", description="This is a test policy area")
    bill = bill_factory(policy_area=policy_area)
    
    assert bill.policy_area == policy_area
    assert bill.policy_area.name == "Test Policy Area"
    
    # Fetch the bill from the database and check the relationship
    fetched_bill = Bill.query.get(bill.id)
    assert fetched_bill.policy_area.name == policy_area.name
    
    logger.info("Completed test_bill_policy_area_relationship")


def test_bill_subject_relationship(bill_factory, subject_factory):
    logger.info("Starting test_bill_subject_relationship")
    
    subject = subject_factory(name="Test Subject")
    bill = bill_factory(subjects=[subject], primary_subject=subject)
    
    assert bill.subjects == [subject]
    assert bill.primary_subject == subject
    
    # Fetch the bill from the database and check the relationship
    fetched_bill = Bill.query.get(bill.id)
    assert fetched_bill.subjects[0].name == subject.name
    assert fetched_bill.primary_subject.name == subject.name
    
    logger.info("Completed test_bill_subject_relationship")


def test_bill_new_fields(bill_factory):
    logger.info("Starting test_bill_new_fields")
    
    bill = bill_factory(congress="117th", bill_type="House Bill")
    
    assert bill.congress == "117th"
    assert bill.bill_type == "House Bill"
    
    # Fetch the bill from the database and check the new fields
    fetched_bill = Bill.query.get(bill.id)
    assert fetched_bill.congress == "117th"
    assert fetched_bill.bill_type == "House Bill"
    
    logger.info("Completed test_bill_new_fields")


def test_bill_to_dict(bill_factory, politician_factory, action_type_factory, policy_area_factory):
    logger.info("Starting test_bill_to_dict")
    
    politician = politician_factory(name="Test Politician")
    action_type = action_type_factory(description='Bill is introduced')
    policy_area = policy_area_factory(name="Test Policy Area", description="This is a test policy area")

    
    bill = bill_factory(sponsor=politician, action_type=action_type, policy_area=policy_area, title="Test Bill")
    
    bill_dict = bill.to_dict()
    
    assert bill_dict['title'] == "Test Bill"
    assert bill_dict['sponsor']['name'] == "Test Politician"
    assert bill_dict['action_type']['description'] == "Bill is introduced"
    assert bill_dict['committee'] == "Test Committee"
    assert bill_dict['voting_record'] == "Voting Record Details"
    assert bill_dict['full_bill_link'] == "http://example.com"
    assert bill_dict['last_action_date'] == "2021-01-01"
    assert bill_dict['update_date'] == "2023-09-12"
    assert bill_dict['policy_area.name'] == "Test Policy Area"
    assert bill_dict['policy_area.description'] == "This is a test policy area"
    assert bill_dict['last_action_description'] == "Test Action Description"
    assert bill_dict['official_title'] == "Test Official Title"
    assert bill_dict['tags'] == "Test Tags"
    assert bill_dict['xml_content'] == {"test_key": "test_value"}
    assert bill_dict['origin_chamber'] == "House"
    assert bill_dict['bill_number'] == "HR001"
    assert bill_dict['status'] == "Proposed"
    assert bill_dict['summary'] == "This is a test bill"
    assert bill_dict['congress'] == "117th"
    assert bill_dict['bill_type'] == "House Bill"
    assert bill_dict['policy_area']['name'] == "Test Policy Area"


    
    logger.info("Completed test_bill_to_dict")
