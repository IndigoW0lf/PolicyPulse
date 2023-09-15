from backend.database.models import Bill, Politician, ActionType, Committee, Amendment, Subject, Action, BillTitle, ActionCode, BillFullText, LOCSummary, LOCSummaryCode, PolicyArea, RelatedBill, CoSponsor, Law, Note, RecordedVote
from config import TestingConfig as config
from datetime import datetime
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_operations import save_to_database
from xml_helper import xml_to_json , get_text, parse_date, version_code_mapping

# Initialize the logger
logging.basicConfig(filename='backend/database/logs/bill_parser.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Create logger instance
logger = logging.getLogger(__name__)

# Configure the database session to interact with the testing database.
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def parse_bill(xml_root):
    with session_scope() as session:
        """
        Parse the bill details from the root element and return a Bill object.
        """
        try:
            bill_details_list = xml_root.xpath('//billStatus/bill')
            if bill_details_list:
                bill_details = bill_details_list[0]
            else:
                logging.error("Error in parse_bill: No bill details found")
                return None
        except Exception as e:
            logging.error(f"Error in parse_bill: {e}")
            return None
        
        try:
            sponsor_details = bill_details.xpath('sponsors/item')[0]
            sponsor = Politician(
                bioguide_id=get_text(sponsor_details, 'bioguideId'),
                full_name=get_text(sponsor_details, 'fullName'),
                first_name=get_text(sponsor_details, 'firstName'),
                last_name=get_text(sponsor_details, 'lastName'),
                state=get_text(sponsor_details, 'state'),
                party=get_text(sponsor_details, 'party'),
                district=get_text(sponsor_details, 'district')
            )
        except Exception as e:
            logging.error(f"Error parsing sponsor details in parse_bill: {e}")
            sponsor = None


        # Parsing title details as per the new logic
        official_title = None
        display_title = None
        try:
            title_elements = bill_details.xpath('titles/item')
            for title_element in title_elements:
                title_type = get_text(title_element, 'titleType')
                if title_type:
                    if 'Official' in title_type:
                        official_title = get_text(title_element, 'title')
                    elif title_type == 'Display Title':
                        display_title = get_text(title_element, 'title')
        except Exception as e:
            logging.error(f"Error parsing title details in parse_bill: {e}")

        
        try:
            bill = Bill(
                bill_number=get_text(bill_details, 'number'),
                bill_type=get_text(bill_details, 'type'),
                congress=get_text(bill_details, 'congress'),
                date_introduced=parse_date(get_text(bill_details, 'introducedDate')),
                full_bill_link=None,  # Placeholder, to be populated from the API data
                last_action_date=parse_date(get_text(bill_details, 'latestAction/actionDate')),
                last_action_description=get_text(bill_details, 'latestAction/text'),
                loc_summary=parse_loc_summaries(bill_details),
                official_title=official_title,
                title=display_title,
                origin_chamber=get_text(bill_details, 'originChamber'),
                policy_area=get_text(bill_details, 'policyArea/name'),
                sponsor=sponsor,
                subjects=parse_subjects(bill_details),
                summary=get_text(bill_details, 'summaries/summary/text'),
                tags=None,  # Placeholder, to be populated later by Langchain
                xml_content=xml_to_json(bill_details),
            )

        except Exception as e:
            logging.error(f"Error creating Bill object in parse_bill: {e}")
            return None

        # Invoke functions to parse related entities and associate them with the bill
        try:
            bill.actions = parse_actions(bill_details)
            bill.amendments = parse_amendments(bill_details)
            bill.committees = parse_committees(bill_details)
            bill.related_bills = parse_related_bills(bill_details)
            bill.cosponsors = parse_cosponsors(bill_details)
            bill.bill_titles = parse_bill_titles(bill_details)
            loc_summaries, loc_summary_codes = parse_loc_summaries(bill_details)
            bill.loc_summaries = loc_summaries
            bill.loc_summary_codes = loc_summary_codes
            bill.notes = parse_notes(bill_details)
            bill.recorded_votes = parse_recorded_votes(bill_details)
        
            session.add(bill)
        
        except Exception as e:
            logging.error(f"Error associating related entities with the Bill object in parse_bill: {e}")

        return bill

def parse_actions(bill_details):
    """Function to parse action details and return a list of Action objects."""
    actions = []
    try:
        for action in bill_details.xpath('actions/item'):
            action_code_value = get_text(action, 'actionCode')

            # Assuming that you have a function to get ActionCode object by its value
            action_code_obj = get_action_code_object(session, action_code_value)


            action_type = ActionType(
                description=get_text(action, 'type'),
                action_code=action_code_obj  # Here, we set the ActionCode object
            )

            action_obj = Action(
                action_date=parse_date(get_text(action, 'actionDate')),
                description=get_text(action, 'text'),
                chamber=get_text(action, 'recordedVotes/recordedVote/chamber'),
                action_type=action_type,
                action_codes=[action_code_obj]  # Here, we associate the ActionCode object with the Action object
            )
            actions.append(action_obj)
    except Exception as e:
        logging.error(f"Error in parse_actions: {e}")

    return actions
    

def get_action_code_object(session, value):
    """Function to get an ActionCode object by its value.

    This function should query the database to get the ActionCode object by its value.
    If not found, it should create a new ActionCode object with the given value.
    """
    try:
        action_code_obj = session.query(ActionCode).filter_by(code=value).first()
        if not action_code_obj:
            action_code_obj = ActionCode(code=value, description="Description for code " + value)
            session.add(action_code_obj)
            # No need to commit here, as the context manager will commit the transaction
    except Exception as e:
        logging.error(f"Error in get_action_code_object: {e}")
        # You might want to re-raise the exception after logging it, to handle it at a higher level
        raise

    return action_code_obj


def parse_amendments(bill_details):
    """Function to parse amendment details and return a list of Amendment objects."""
    amendments = []
    try:
        for amendment in bill_details.xpath('amendments/amendment'):
            amendment_obj = Amendment(
                amendment_number=get_text(amendment, 'number'),
                congress=get_text(amendment, 'congress'),
                description=get_text(amendment, 'description'),
                latest_action_date=parse_date(get_text(amendment, 'latestAction/actionDate')),
                latest_action_text=get_text(amendment, 'latestAction/text'),
                purpose=get_text(amendment, 'purpose'),
                type=get_text(amendment, 'type'),
                status=get_text(amendment, 'status'),
            )
            amendments.append(amendment_obj)
    except Exception as e:
        logging.error(f"Error in parse_amendments: {e}")
        # Optionally re-raise the exception
        raise

    return amendments
    

def parse_bill_titles(bill_details):
    """Function to parse bill titles and return a list of BillTitle objects."""
    bill_titles = []
    try:
        for title in bill_details.xpath('titles/item'):
            bill_title_obj = BillTitle(
                title_type=get_text(title, 'titleType'),
                title_text=get_text(title, 'title'),
                chamber_code=get_text(title, 'chamberCode'),
                chamber_name=get_text(title, 'chamberName'),
            )
            bill_titles.append(bill_title_obj)
    except Exception as e:
        logging.error(f"Error in parse_bill_titles: {e}")
        # Optionally re-raise the exception
        raise

    return bill_titles


def parse_committees(bill_details):
    """Function to parse committee details and return a list of Committee objects."""
    committees = []
    try:
        for committee in bill_details.xpath('committees/item'):
            committee_obj = Committee(
                name=get_text(committee, 'name'),
                chamber=get_text(committee, 'chamber'),
                committee_code=get_text(committee, 'systemCode'),
            )
            committees.append(committee_obj)
    except Exception as e:
        logging.error(f"Error in parse_committees: {e}")
        # Optionally re-raise the exception
        raise
    return committees


def parse_cosponsors(bill_details):
    """Function to parse cosponsor details and return a list of CoSponsor objects."""
    cosponsors = []
    try:
        for cosponsor in bill_details.xpath('cosponsors/item'):
            cosponsor_obj = CoSponsor(
                bioguide_id=get_text(cosponsor, 'bioguideId'),
                full_name=get_text(cosponsor, 'fullName'),
                first_name=get_text(cosponsor, 'firstName'),
                last_name=get_text(cosponsor, 'lastName'),
                party=get_text(cosponsor, 'party'),
                state=get_text(cosponsor, 'state'),
                sponsorship_date=parse_date(get_text(cosponsor, 'sponsorshipDate')),
                is_original_cosponsor=get_text(cosponsor, 'isOriginalCosponsor') == 'true',
                sponsorship_withdrawn_date=parse_date(get_text(cosponsor, 'sponsorshipWithdrawnDate')),
            )
            cosponsors.append(cosponsor_obj)
    except Exception as e:
        logging.error(f"Error in parse_cosponsors: {e}")
        # Optionally re-raise the exception
        raise
    return cosponsors


def parse_laws(bill_details):
    """Function to parse laws and return a list of Law objects."""
    laws = []
    try:
        for item in bill_details.xpath('laws/item'):
            law_type = get_text(item, 'type')
            law_number = get_text(item, 'number')
            if law_type and law_number:
                law_obj = Law(type=law_type, number=law_number)
                laws.append(law_obj)
    except Exception as e:
        logging.error(f"Error in parse_laws: {e}")
        # Optionally re-raise the exception
        raise
    return laws


def parse_loc_summaries(bill_details):
    """Function to parse LOC summary details and return a list of LOCSummary and LOCSummaryCode objects."""
    loc_summaries = []
    loc_summary_codes = []
    try:
        for summary in bill_details.xpath('summaries/summary'):
            version_code = get_text(summary, 'versionCode')
            text = get_text(summary, 'text')
            
            # Get chamber and action description from version code mapping
            chamber = version_code_mapping.get(version_code, {}).get('chamber', '')
            action_desc = version_code_mapping.get(version_code, {}).get('action_desc', '')

            # Create LOCSummaryCode object
            loc_summary_code = LOCSummaryCode(
                version_code=version_code,
                chamber=chamber,
                action_desc=action_desc
            )
            loc_summary_codes.append(loc_summary_code)
            
            # Create LOCSummary object
            loc_summary = LOCSummary(
                versions={'version_code': version_code, 'text': text},
                loc_summary_code=loc_summary_code  # Linking with LOCSummaryCode
            )
            loc_summaries.append(loc_summary)
    except Exception as e:
        logging.error(f"Error in parse_loc_summaries: {e}")
        # Optionally re-raise the exception
        raise
    return loc_summaries, loc_summary_codes

def parse_notes(bill_details):
    """Function to parse notes and return a list of Note objects."""
    notes = []
    try:
        for item in bill_details.xpath('notes/item'):
            note_text = get_text(item, 'text')
            if note_text:
                note_obj = Note(text=note_text)
                notes.append(note_obj)
    except Exception as e:
        logging.error(f"Error in parse_notes: {e}")
        # Optionally re-raise the exception
        raise
    return notes

def parse_recorded_votes(bill_details):
    """Function to parse recorded votes and return a list of RecordedVote objects."""
    recorded_votes = []
    try:
        for item in bill_details.xpath('actions/item/recordedVotes/recordedVote'):
            roll_number = get_text(item, 'rollNumber')
            url = get_text(item, 'url')
            chamber = get_text(item, 'chamber')
            congress = get_text(item, 'congress')
            date = parse_date(get_text(item, 'date'))
            session_number = get_text(item, 'sessionNumber')
            if roll_number and url and chamber and congress and date and session_number:
                recorded_vote_obj = RecordedVote(
                    roll_number=roll_number,
                    url=url,
                    chamber=chamber,
                    congress=congress,
                    date=date,
                    session_number=session_number
                )
                recorded_votes.append(recorded_vote_obj)
    except Exception as e:
        logging.error(f"Error in parse_recorded_votes: {e}")
        # Optionally re-raise the exception
        raise
    return recorded_votes


def parse_related_bills(bill_details):
    """Function to parse related bills and return a list of RelatedBill objects."""
    related_bills = []
    try:
        for related_bill in bill_details.xpath('relatedBills/item'):
            related_bill_obj = RelatedBill(
                title=get_text(related_bill, 'title'),
                congress=get_text(related_bill, 'congress'),
                number=get_text(related_bill, 'number'),
                type=get_text(related_bill, 'type'),
                latest_action_date=parse_date(get_text(related_bill, 'latestAction/actionDate')),
                latest_action_text=get_text(related_bill, 'latestAction/text'),
            )
            related_bills.append(related_bill_obj)
    except Exception as e:
        logging.error(f"Error in parse_related_bills: {e}")
        # Optionally re-raise the exception
        raise
    return related_bills

def parse_subjects(bill_details):
    """Function to parse legislative subjects and return a list of Subject objects."""
    subjects = []
    try:
        for item in bill_details.xpath('subjects/legislativeSubjects/item'):
            subject_name = get_text(item, 'name')
            if subject_name:
                subject_obj = Subject(name=subject_name)
                subjects.append(subject_obj)
    except Exception as e:
        logging.error(f"Error in parse_subjects: {e}")
        # Optionally re-raise the exception
        raise
    return subjects

    


