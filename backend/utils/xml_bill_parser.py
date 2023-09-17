from backend.database.models import Bill, Politician, ActionType, Committee, Amendment, Subject, Action, BillTitle, ActionCode, LOCSummary, PolicyArea, LOCSummaryCode, RelatedBill, CoSponsor, Law, Note, RecordedVote
from config import TestingConfig as config
from datetime import datetime
from lxml import etree
import logging
from contextlib import contextmanager
from backend.utils.xml_helper import xml_to_json , get_text, parse_date, version_code_mapping
from backend.utils.database import SessionFactory


logging.basicConfig(filename='backend/database/logs/bill_parser.log', level=logging.WARNING,
                    format='%(asctime)s:%(levelname)s:%(message)s')


# Create logger instance
logger = logging.getLogger(__name__)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionFactory() 
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def parse_bill(xml_root, session):
    """
    Parse the bill details from the XML root element and return a Bill object.
    
    Parameters:
    xml_root (xml.etree.ElementTree.Element): The root element of the XML data.
    session (sqlalchemy.orm.session.Session): The database session for querying and adding data.
    
    Returns:
    Bill: A Bill object with the parsed data, or None if an error occurred.
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
    
    main_bill_number = get_text(bill_details, 'number')
    
    try:
        sponsor_details = bill_details.xpath('sponsors/item')[0]
        sponsor = Politician(
            bioguide_id=get_text(sponsor_details, 'bioguideId'),
            name=get_text(sponsor_details, 'fullName'),
            first_name=get_text(sponsor_details, 'firstName'),
            last_name=get_text(sponsor_details, 'lastName'),
            state=get_text(sponsor_details, 'state'),
            party=get_text(sponsor_details, 'party'),
            district=get_text(sponsor_details, 'district')
        )
    except Exception as e:
        logging.error(f"Error parsing sponsor details in parse_bill: {e}")
        sponsor = None
        raise

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
        raise

    try:
        bill_number = get_text(bill_details, 'number')
        
        # Check if a bill with the same number already exists
        bill = session.query(Bill).filter_by(bill_number=bill_number).first()
        
        # If the bill doesn't exist, create a new Bill object
        if not bill:
            bill = Bill(bill_number=bill_number)

        # Now, populate or update the fields of the bill object
        introduced_date_str = str(get_text(bill_details, 'introducedDate'))
        last_action_date_str = str(get_text(bill_details, 'latestAction/actionDate'))
        
        bill.bill_type = get_text(bill_details, 'type')
        bill.full_bill_link = None  # Placeholder, to be populated from the API data
        bill.congress = get_text(bill_details, 'congress')
        bill.date_introduced = parse_date(introduced_date_str)
        bill.last_action_date = parse_date(last_action_date_str)
        bill.last_action_description = get_text(bill_details, 'latestAction/text')
        bill.official_title = official_title
        bill.origin_chamber = get_text(bill_details, 'originChamber')
        bill.sponsor = sponsor
        bill.subjects = parse_subjects(session, bill_details)
        bill.summary = get_text(bill_details, 'summaries/summary/text/CDATA')
        bill.tags = None  # Placeholder, to be populated later
        bill.title = display_title
        bill.xml_content = xml_to_json(etree.tostring(bill_details))
        
        session.add(bill)
        session.flush()
        bill_id = bill.id

    except Exception as e:
        logging.error(f"Error creating/updating Bill object in parse_bill: {e}")
        return None

    # Invoke functions to parse related entities and associate them with the bill
    try:
    
        bill.actions = parse_actions(session, bill_details, bill_id)
        bill.amendments = parse_amendments(session, bill_details, bill_id)
        bill.committees = parse_committees(session, bill_details)
        bill.related_bills = parse_related_bills(session, bill_details, bill_id)
        bill.cosponsors = parse_cosponsors(session, bill_details, bill_id)
        bill.bill_titles = parse_bill_titles(session, bill_details, bill_id)
        bill.notes = parse_notes(session, bill_details, bill_id)
        bill.recorded_votes = parse_recorded_votes(session, bill_details, bill_id)
        bill.laws = parse_laws(session, bill_details, bill_id)
        bill.loc_summary = parse_loc_summaries(session, bill_details, bill_id)  
        

        session.add(bill)
        session.commit()
    except Exception as e:
        logging.error(f"Error associating related entities with the Bill object in parse_bill: {e}")
        print("Bill parsing failed.")
        return None

    return bill
    

def get_action_type_object(session, description, action_description):
    """Function to get an ActionType object by its description.

    This function queries the database to find an ActionType object 
    based on the description provided. If the ActionType does not exist, 
    it creates a new one.
    """
    try:
        action_type_obj = session.query(ActionType).filter_by(description=description).first()
        if not action_type_obj:
            action_type_obj = ActionType(description=description, action_type=action_description)
            session.add(action_type_obj)
            session.flush()  # This is to ensure that the new object gets an ID
    except Exception as e:
        logging.error(f"Error in get_action_type_object: {e}")
        raise
    return action_type_obj


def parse_actions(session, bill_details, bill_id):
    actions = []
    try:
        for action in bill_details.xpath('actions/item'):
            action_code_value = get_text(action, 'actionCode')
            action_code_obj = get_action_code_object(session, action_code_value)

            action_type_description = get_text(action, 'type')
            action_description = get_text(action, 'text')
            action_type_obj = get_action_type_object(session, action_type_description, action_description)

            action_obj = Action(
                action_date=parse_date(get_text(action, 'actionDate')),
                description=action_description,
                chamber=get_text(action, 'recordedVotes/recordedVote/chamber'),
                action_type=action_type_obj,  
                action_codes=[action_code_obj],
                bill_id=bill_id
            )
            actions.append(action_obj)
            session.add(action_obj)
        session.flush()
    except Exception as e:
        logging.error(f"Error in parse_actions: {e}", exc_info=True)
        raise
    return actions


def get_action_code_object(session, code):
    """Function to get an ActionCode object by its code.
    
    This function queries the database to find an ActionCode object 
    based on the code provided. If the ActionCode does not exist, 
    it creates a new one.
    """
    try:
        action_code_obj = session.query(ActionCode).filter_by(code=code).first()
        if not action_code_obj:
            action_code_obj = ActionCode(code=code)
            session.add(action_code_obj)
            session.flush()  # This is to ensure that the new object gets an ID
    except Exception as e:
        logging.error(f"Error in get_action_code_object: {e}")
        raise
    return action_code_obj


def parse_amendments(session, bill_details, bill_id):
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
                bill_id=bill_id,
            )
            amendments.append(amendment_obj)
    except Exception as e:
        logging.error(f"Error in parse_amendments: {e}")
        # Optionally re-raise the exception
        raise
    return amendments
    

def parse_bill_titles(session, bill_details, bill_id):
    """Function to parse bill titles and return a list of BillTitle objects."""
    bill_titles = []
    try:
        for title in bill_details.xpath('titles/item'):
            bill_title_obj = BillTitle(
                title_type=get_text(title, 'titleType'),
                title_text=get_text(title, 'title'),
                chamber_code=get_text(title, 'chamberCode'),
                chamber_name=get_text(title, 'chamberName'),
                bill_id=bill_id,
            )
            bill_titles.append(bill_title_obj)
    except Exception as e:
        logging.error(f"Error in parse_bill_titles: {e}")
        # Optionally re-raise the exception
        raise
    return bill_titles


def parse_committees(session, bill_details):
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


def parse_cosponsors(session, bill_details, bill_id):
    """Function to parse cosponsor details and return a list of CoSponsor objects."""
    cosponsors = []
    try:
        for cosponsor in bill_details.xpath('cosponsors/item'):
            bioguide_id = get_text(cosponsor, 'bioguideId')
            
            # Get or create the Politician object based on the bioguide_id
            politician = get_or_create_politician(session, bioguide_id, cosponsor)
            
            cosponsor_obj = CoSponsor(
                politician_id=politician.id,  # Set the politician_id on the CoSponsor object
                sponsorship_date=parse_date(get_text(cosponsor, 'sponsorshipDate')),
                is_original_cosponsor=get_text(cosponsor, 'isOriginalCosponsor') == 'true',
                sponsorship_withdrawn_date=parse_date(get_text(cosponsor, 'sponsorshipWithdrawnDate')),
                bill_id=bill_id,
            )
            cosponsors.append(cosponsor_obj)
    except Exception as e:
        logging.error(f"Error in parse_cosponsors: {e}")
        # Optionally re-raise the exception
        raise
    return cosponsors


def get_or_create_politician(session, bioguide_id, cosponsor_details):
    """Function to get or create a Politician object based on the bioguide_id."""
    try:
        politician = session.query(Politician).filter_by(bioguide_id=bioguide_id).first()
        if not politician:
            politician = Politician(
                bioguide_id=bioguide_id,
                name=get_text(cosponsor_details, 'fullName'),
                first_name=get_text(cosponsor_details, 'firstName'),
                last_name=get_text(cosponsor_details, 'lastName'),
                party=get_text(cosponsor_details, 'party'),
                state=get_text(cosponsor_details, 'state'),
                district=get_text(cosponsor_details, 'district')
            )
            session.add(politician)
            session.flush()
    except Exception as e:
        logging.error(f"Error in get_or_create_politician: {e}")
        raise

    return politician


def parse_laws(session, bill_details, bill_id):
    """Function to parse laws and return a list of Law objects."""
    laws = []
    try:
        for item in bill_details.xpath('laws/item'):
            law_type = get_text(item, 'type')
            law_number = get_text(item, 'number')
            if law_type and law_number:
                law_obj = Law(type=law_type, number=law_number, bill_id=bill_id)
                laws.append(law_obj)
    except Exception as e:
        logging.error(f"Error in parse_laws: {e}")
        # Optionally re-raise the exception
        raise
    return laws


def parse_loc_summaries(session, bill_details, bill_id):
    loc_summary_codes = []
    versions = []
    logging.info("Entering parse_loc_summaries function")
    
    try:
        with session.no_autoflush:
            # Query all existing LOCSummaryCodes and store them in a dictionary
            existing_codes = {code.version_code: code for code in session.query(LOCSummaryCode).all()}

            for summary in bill_details.xpath('summaries/summary'):
                version_code = get_text(summary, 'versionCode')
                text = get_text(summary, 'text')
                
                # Get chamber and action description from version code mapping
                chamber = version_code_mapping.get(version_code, {}).get('chamber', '')
                action_desc = version_code_mapping.get(version_code, {}).get('action_desc', '')

                # Check if a LOCSummaryCode with the extracted version_code already exists in the database
                loc_summary_code = existing_codes.get(version_code)
                
                # If not, create a new LOCSummaryCode object and add it to the session
                if not loc_summary_code:
                    loc_summary_code = LOCSummaryCode(
                        version_code=version_code,
                        chamber=chamber,
                        action_desc=action_desc
                    )
                    session.add(loc_summary_code)
                    
                    logging.info("Created new LOCSummaryCode object and added it to the session")

                loc_summary_codes.append(loc_summary_code)
                
                # Append version details to versions list
                versions.append({'version_code': version_code, 'text': text})
    except Exception as e:
        logging.error(f"Error in parse_loc_summaries: {e}")
        raise

    logging.info(f"Bill ID before creating LOCSummary: {bill_id}")
    
    # Create a single LOCSummary object with all the versions and summary codes
    loc_summary = LOCSummary(
        versions=versions,
        loc_summary_codes=loc_summary_codes,
        bill_id=bill_id
    )

    session.add(loc_summary)  # Adding loc_summary to the session here
    session.flush()  # Added session.flush() to synchronize the session's state with the database
    logging.info("Before calling to_dict in parse_loc_summaries")
    logging.info(f"Created new LOCSummary: {loc_summary.to_dict()}")  # New log statement
    logging.info("After calling to_dict in parse_loc_summaries")
    
    logging.info("Exiting parse_loc_summaries function")
    
    return loc_summary


def parse_notes(session, bill_details, bill_id):
    """Function to parse notes and return a list of Note objects."""
    notes = []
    try:
        for item in bill_details.xpath('notes/item'):
            note_text = get_text(item, 'text')
            bill_id=bill_id
            if note_text:
                note_obj = Note(text=note_text)
                notes.append(note_obj)
    except Exception as e:
        logging.error(f"Error in parse_notes: {e}")
        # Optionally re-raise the exception
        raise
    return notes


def parse_policy_area(session, bill_details, bill_id):
    try:
        policy_area_name = get_text(bill_details, 'policyArea/name')
        existing_policy_area = session.query(PolicyArea).filter_by(name=policy_area_name).first()

        if existing_policy_area:
            existing_policy_area.bill_id = bill_id
            policy_area = existing_policy_area  # Assign existing policy area to the policy_area variable
        else:
            policy_area = PolicyArea(name=policy_area_name, bill_id=bill_id)
            session.add(policy_area)
        
        session.flush()
        return policy_area
    except Exception as e:
        logging.error(f"Error in parse_policy_area: {e}")
        raise


def parse_recorded_votes(session, bill_details, bill_id):
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
                    session_number=session_number,
                    bill_id=bill_id
                )
                recorded_votes.append(recorded_vote_obj)
    except Exception as e:
        logging.error(f"Error in parse_recorded_votes: {e}")
        # Optionally re-raise the exception
        raise
    return recorded_votes


def parse_related_bills(session, bill_details, bill_id):
    related_bills = []
    try:
        for related_bill in bill_details.xpath('relatedBills/item'):
            related_bill_number = get_text(related_bill, 'number')
            congress = get_text(related_bill, 'congress')
            type = get_text(related_bill, 'type')
            title = get_text(related_bill, 'title')
            latest_action_date = parse_date(get_text(related_bill, 'latestAction/actionDate'))
            latest_action_text = get_text(related_bill, 'latestAction/text')
            relationship_type = get_text(related_bill, 'relationshipDetails/item/type')
            relationship_identified_by = get_text(related_bill, 'relationshipDetails/item/identifiedBy')
            
            related_bill_obj = RelatedBill(
                main_bill_id=bill_id,
                related_bill_number=related_bill_number,
                congress=congress,
                type=type,
                title=title,
                latest_action_date=latest_action_date,
                latest_action_text=latest_action_text,
                relationship_type=relationship_type,
                relationship_identified_by=relationship_identified_by,
            )
            related_bills.append(related_bill_obj)
    except Exception as e:
        logging.error(f"Error in parse_related_bills: {e}")
        # Optionally re-raise the exception
        raise
    return related_bills


def parse_subjects(session, bill_details):
    subjects = []
    try:
        for item in bill_details.xpath('subjects/legislativeSubjects/item'):
            subject_name = get_text(item, 'name')
            
            # Check if a subject with the extracted name already exists in the database
            subject = session.query(Subject).filter_by(name=subject_name).first()
            
            # If not, create a new Subject object and add it to the session
            if not subject:
                subject = Subject(
                    name=subject_name,
                )
                session.add(subject)
                session.flush()  
            
            subjects.append(subject)
    except Exception as e:
        logging.error(f"Error in parse_subjects: {e}")
        raise

    return subjects