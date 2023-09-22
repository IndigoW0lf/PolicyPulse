from backend.database.models import Action, ActionCode, ActionType, Amendment, AmendmentAction, AmendmentLink, AmendedBill, Bill, BillRelationship, BillTitle, CoSponsor, Committee, Law, LOCSummary, LOCSummaryCode, Note, PolicyArea, Politician, RecordedVote, RelatedBill, Subject, Subcommittee
from config import TestingConfig as config
from lxml import etree, html
import logging
from contextlib import contextmanager
from backend.utils.xml_helper import xml_to_json, get_text, parse_date, version_code_mapping
from backend.utils.database import SessionFactory
import re
from datetime import datetime
import traceback
from sqlalchemy import and_


# Initialize the logger
logging.basicConfig(filename='backend/database/logs/bill_parser.log',
                    level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

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
    logging.info("starting to parse bill")
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

    try:
        sponsor_details_list = bill_details.xpath('sponsors/item')
        if sponsor_details_list:
            sponsor_details = sponsor_details_list[0]
        else:
            logging.error("No sponsor details found")
        # handle error
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
        congress_session = get_text(bill_details, 'congress')

        # Validate the data
        if not bill_number or not congress_session:
            raise ValueError(
                f"Invalid data: bill_number={bill_number}, congress_session={congress_session}")

        # Create a new Bill object directly without checking for duplicates
        bill = Bill(bill_number=bill_number, congress=congress_session)

        # Now, populate or update the fields of the bill object
        introduced_date_str = str(get_text(bill_details, 'introducedDate'))
        last_action_date_str = str(
            get_text(bill_details, 'latestAction/actionDate'))

        # Set fields based on above logic
        bill.official_title = official_title
        bill.sponsor = sponsor
        bill.title = display_title

        # Set fields based on conversions or parsing
        bill.status = get_latest_bill_status(bill_details) 
        bill.bill_type = get_text(bill_details, 'type')
        bill.committee = get_text(bill_details, 'committees/item/name')
        bill.congress = get_text(bill_details, 'congress')
        bill.date_introduced = parse_date(introduced_date_str)
        bill.last_action_date = parse_date(last_action_date_str)
        bill.last_action_description = get_text(bill_details, 'latestAction/text')
        bill.origin_chamber = get_text(bill_details, 'originChamber')
        bill.subjects = parse_subjects(session, bill_details)
        bill.update_date = parse_date(get_text(bill_details, 'summaries/summary/updateDate'))
        bill.xml_content = xml_to_json(etree.tostring(bill_details))
        bill.full_bill_link = None  # Placeholder, to be populated from the API data
        bill.tags = None  # Placeholder, to be populated later

        session.add(bill)
        session.flush()
        bill_id = bill.id

    except Exception as e:
        logging.error(
            f"Error creating/updating Bill object in parse_bill: {e}")
        return None

    # Invoke functions to parse related entities and associate them with the bill
    try:

        bill.bill_titles = parse_bill_titles(session, bill_details, bill_id)
        bill.actions = parse_actions(session, bill_details, bill_id)
        amendments = parse_amendments(session, bill_details, bill_id)
        bill.amendments = amendments
        bill.amended_bill = parse_amended_bill(session, bill_details, amendments)
        bill.amendment_links = parse_amendment_links(session, bill_details, bill_id)
        bill.amendment_actions = parse_amendment_actions(session, bill_details, bill_id)
        bill.committees = parse_committees(session, bill_details)
        bill.related_bills = parse_related_bills(session, bill_details, bill_id)
        bill.co_sponsors = parse_cosponsors(session, bill_details, bill_id)
        bill.notes = parse_notes(session, bill_details, bill_id)
        bill.subcommittees = parse_subcommittees(session, bill_details)
        bill.policy_area = parse_policy_area(session, bill_details, bill_id)
        bill.recorded_votes = parse_recorded_votes(session, bill_details, bill_id)
        bill.laws = parse_laws(session, bill_details, bill_id)
        bill.loc_summary = parse_loc_summaries(session, bill_details, bill_id)

        session.add(bill)
        logging.info(
            f"Bill object before commit in parse_bill: {bill.to_dict() if bill else None}")
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(
            f"Error in parse_bill: {e}, Bill object: {bill.to_dict() if bill else None}")
        return None

    logging.info(
        f"Bill object at the end of parse_bill: {bill.to_dict() if bill else None}")
    return bill


def get_action_type_object(session, description, action_description):
    """Function to get an ActionType object by its description.

    This function queries the database to find an ActionType object 
    based on the description provided. If the ActionType does not exist, 
    it creates a new one.
    """
    try:
        action_type_obj = session.query(ActionType).filter_by(
            description=description).first()
        if not action_type_obj:
            action_type_obj = ActionType(
                description=description, action_type=action_description)
            session.add(action_type_obj)
            session.flush()  # This is to ensure that the new object gets an ID
            logging.info(
                f"New ActionType object created: {action_type_obj.description}")
    except Exception as e:
        logging.error(f"Error in get_action_type_object: {e}")
        raise
    return action_type_obj


def parse_actions(session, bill_details, bill_id):
    logging.info(
        f"Starting parsing actions with bill_id in parse_actions: {bill_id}")
    actions = []
    try:
        for action in bill_details.xpath('actions/item'):
            logging.info(f"Action node: {etree.tostring(action)}")

            action_code_value = get_text(action, 'actionCode')
            action_code_obj = get_action_code_object(
                session, action_code_value)
            session.add(action_code_obj)

            action_type_description = get_text(action, 'type')
            action_description = get_text(action, 'text')
            action_type_obj = get_action_type_object(
                session, action_type_description, action_description)
            session.add(action_type_obj)

            # Extract yea-nay vote counts and record vote number
            yea_nay_match = re.search(
                r'Yea-Nay Vote\. (\d+) - (\d+)\. Record Vote Number: (\d+)\.', action_description)
            if yea_nay_match:
                yea_votes, nay_votes, record_vote_number = map(
                    int, yea_nay_match.groups())
            else:
                yea_votes, nay_votes, record_vote_number = None, None, None

            action_type_obj = get_action_type_object(
                session, action_type_description, action_description)

            action_obj = Action(
                action_date=parse_date(get_text(action, 'actionDate')),
                description=action_description,
                chamber=get_text(action, 'sourceSystem/name'),
                action_type=action_type_obj,
                action_codes=[action_code_obj],
                yea_votes=yea_votes,
                nay_votes=nay_votes,
                record_vote_number=record_vote_number,
                bill_id=bill_id
            )
            actions.append(action_obj)
            logging.info(f"Action object created and added: {action_obj}")
            session.add(action_obj)

        # Find the action with the latest date
        latest_action = max(actions, key=lambda action: action.action_date)
        latest_action.is_latest = True

        session.commit()
    except Exception as e:
        logging.error(f"Error in parse_actions: {e}", exc_info=True)
        raise

    logging.info(
        f"Finished parsing actions with bill_id in parse_actions: {bill_id}")
    return actions

def get_latest_bill_status(bill_details):
    """Extract the latest bill status based on the newest actionDate."""
    # Extract all actions from the bill details
    actions = bill_details.findall('actions/item')

    # If there are no actions, return None or a default status
    if not actions:
        return None

    # Sort the actions based on actionDate in descending order
    sorted_actions = sorted(actions, key=lambda action: action.findtext('actionDate'), reverse=True)

    # Get the latest action (first item after sorting in descending order)
    latest_action = sorted_actions[0]

    # Extract the status text from the latest action
    latest_status = latest_action.findtext('text')

    return latest_status

def get_action_code_object(session, code):
    """Function to get an ActionCode object by its code.

    This function queries the database to find an ActionCode object 
    based on the code provided. If the ActionCode does not exist, 
    it creates a new one.
    """
    logging.info(f"Starting get_action_code_object with code: {code}")
    try:
        action_code_obj = session.query(
            ActionCode).filter_by(code=code).first()
        logging.info(f"Action code object found: {action_code_obj}")
        if not action_code_obj:
            action_code_obj = ActionCode(code=code)
            session.add(action_code_obj)
            logging.info(
                f"New ActionCode object created and added: {action_code_obj.code}")
            session.flush()  # This is to ensure that the new object gets an ID
    except Exception as e:
        logging.error(f"Error in get_action_code_object: {e}")
        raise
    logging.info(f"Finished get_action_code_object with code: {code}")
    return action_code_obj


def parse_amendments(session, bill_details, bill_id):
    logging.info(f"Starting to parse amendments for bill_id: {bill_id}")
    """Function to parse amendment details and return a list of Amendment objects."""
    amendments = []
    try:
        for amendment in bill_details.xpath('amendments/amendment'):
            bioguide_id = get_text(amendment, 'sponsor/item/bioguideId')
            politician = session.query(Politician).filter_by(
                bioguide_id=bioguide_id).first()

            if not politician:
                # Create new Politician record
                politician = Politician(
                    name=get_text(amendment, 'sponsors/item/name'),
                    first_name=get_text(amendment, 'sponsors/item/firstName'),
                    last_name=get_text(amendment, 'sponsors/item/lastName'),
                    state=get_text(amendment, 'sponsors/item/state'),
                    district=get_text(amendment, 'sponsors/item/district'),
                    party=get_text(amendment, 'sponsors/item/party'),
                    bioguide_id=get_text(
                        amendment, 'sponsors/item/bioguideId'),
                )
                session.add(politician)
                session.commit()

            sponsor_id = politician.id

            amendment_obj = Amendment(
                amendment_number=get_text(amendment, 'number'),
                congress=get_text(amendment, 'congress'),
                description=get_text(amendment, 'description'),
                latest_action_date=parse_date(
                    get_text(amendment, 'latestAction/actionDate')),
                latest_action_text=get_text(amendment, 'latestAction/text'),
                purpose=get_text(amendment, 'purpose'),
                type=get_text(amendment, 'type'),
                sponsor_id=sponsor_id,
                status=get_text(amendment, 'actions/actions/item/text'),
                bill_id=bill_id,
            )
            amendments.append(amendment_obj)
            session.add(amendment_obj)
            logging.debug(f"Before flush: Amendment ID is {amendment_obj.id}")
            session.flush()
            logging.debug(f"After flush: Amendment ID is {amendment_obj.id}")

            # Now parse the actions associated with this amendment
            amendment_obj.actions = parse_amendment_actions(
                session, amendment, amendment_obj.id)
            logging.info(
                f"Parsed actions for amendment_id: {amendment_obj.id}")
    except Exception as e:
        logging.error(f"Error in parse_amendments: {e}")
        # Optionally re-raise the exception
        raise
    logging.info(f"Finished parsing amendments for bill_id: {bill_id}")
    return amendments


def parse_amendment_actions(session, bill_details, amendment_id):
    """Function to parse amendment action details and return a list of AmendmentAction objects."""
    logging.info(f"Starting to parse actions for amendment_id: {amendment_id}")
    amendment_actions = []
    try:
        # Loop through the action elements in the amendment_details (XML node)
        for action in bill_details.xpath('actions/actions/item'):
            action_code = get_text(action, 'actionCode')
            action_date = parse_date(get_text(action, 'actionDate'))
            action_time = get_text(action, 'actionTime')
            action_text = get_text(action, 'text')
            committee_name = get_text(action, 'sourceSystem/name')
            committee_system_code = get_text(action, 'sourceSystem/code')

            amendment_action = AmendmentAction(
                action_code=action_code,
                action_date=action_date,
                action_time=action_time,
                committee_name=committee_name,
                committee_system_code=committee_system_code,
                action_text=action_text,
                amendment_id=amendment_id
            )
            amendment_actions.append(amendment_action)
            # Moved this line inside the for loop
            session.add(amendment_action)

        session.flush()  # Moved this line outside the for loop
        logging.info(
            f"Finished parsing {len(amendment_actions)} actions for amendment_id: {amendment_id}")
    except Exception as e:
        logging.error(f"Error in parse_amendment_actions: {e}")
        raise
    return amendment_actions


def parse_amended_bill(session, bill_details, amendments):
    logging.info("Starting to parse amended bills")
    amended_bills = []
    try:
        for index, amended_bill_detail in enumerate(bill_details.xpath('amendments/amendment')):
            amended_bill_data = amended_bill_detail.xpath('amendedBill')[0]

            amended_bill_obj = AmendedBill(
                congress=get_text(amended_bill_data, 'congress'),
                origin_chamber=get_text(amended_bill_data, 'originChamber'),
                origin_chamber_code=get_text(
                    amended_bill_data, 'originChamberCode'),
                title=get_text(amended_bill_data, 'title'),
                type=get_text(amended_bill_data, 'type'),
                # Pass the Amendment object, not its ID
                amendment=amendments[index]
            )
            logging.info(
                f"Amended bill object after creation: {amended_bill_obj}")
            amended_bills.append(amended_bill_obj)
            session.add(amended_bill_obj)
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Error in parse_amended_bill: {e}")
        # Optionally re-raise the exception
        raise
    logging.info("Finished parsing amended bills")
    return amended_bills


def parse_amendment_links(session, bill_details, bill_id):
    """Function to parse amendment links and return a list of AmendmentLink objects."""
    logging.info(f"Starting to parse amendment links for bill_id: {bill_id}")
    amendment_links = []
    try:
        # Get the amendments with their IDs
        amendments = parse_amendments(session, bill_details, bill_id)
        for amendment in amendments:
            amendment_id = amendment.id  # Get the ID of the current amendment
            # Log the amendment ID
            logging.info(f"Processing amendment ID: {amendment_id}")

            # Get the XML node for the current amendment using the amendment number
            amendment_node = bill_details.xpath(
                f'//amendments/amendment[number="{amendment.amendment_number}"]')[0]

            # Get links for the current amendment
            for link in amendment_node.xpath('links/link'):
                name = get_text(link, 'name')
                url = get_text(link, 'url')

                # Log the link details
                logging.info(f"Parsing link: name={name}, url={url}")

                amendment_link_obj = AmendmentLink(
                    name=name,
                    url=url,
                    amendment_id=amendment_id
                )
                amendment_links.append(amendment_link_obj)
                # Add the object to the session
                session.add(amendment_link_obj)
                logging.info(
                    f"AmendmentLink object created and added: {amendment_link_obj}")
        session.commit()
    except Exception as e:
        logging.error(f"Error in parse_amendment_links: {e}")
        # Optionally re-raise the exception
        raise
    logging.info(f"Finished parsing amendment links for bill_id: {bill_id}")
    return amendment_links


def parse_bill_titles(session, bill_details, bill_id):
    """Function to parse bill titles and return a list of BillTitle objects."""
    bill_titles = []
    try:
        for title in bill_details.xpath('titles/item'):
            title_type = get_text(title, 'titleType')
            title_text = get_text(title, 'title')
            chamber_code = get_text(title, 'chamberCode')
            chamber_name = get_text(title, 'chamberName')

            logging.info(
                f"Parsing title item: Type: {title_type}, Text: {title_text}, Chamber Code: {chamber_code}, Chamber Name: {chamber_name}")

            bill_title_obj = BillTitle(
                title_type=title_type,
                title_text=title_text,
                chamber_code=chamber_code,
                chamber_name=chamber_name,
                bill_id=bill_id,
            )
            bill_titles.append(bill_title_obj)
            session.add(bill_title_obj)
        session.commit()
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
            committee_code = get_text(committee, 'systemCode')

            # Create or get the Committee object
            committee_obj = session.query(Committee).filter(
                and_(
                    Committee.committee_code == committee_code,
                    Committee.name == get_text(committee, 'name')
                )
            ).first()

            if not committee_obj:
                committee_obj = Committee(
                    name=get_text(committee, 'name'),
                    chamber=get_text(committee, 'chamber'),
                    committee_code=committee_code,
                )
                committees.append(committee_obj)
                session.add(committee_obj)  # Add committee object to session
                logging.info(
                    f"Committee object created: {committee_obj.name} - {committee_obj.committee_code}")
            else:
                logging.info(
                    f"Committee object found in database: {committee_obj.name} - {committee_obj.committee_code}")

        session.commit()
        logging.info("Committee objects committed to database")

    except Exception as e:
        logging.error(f"Error in parse_committees: {e}")
        session.rollback()
        raise

    return committees


def parse_subcommittees(session, bill_details):
    subcommittees = []
    try:
        for committee in bill_details.xpath('committees/item'):
            committee_code = get_text(committee, 'systemCode')
            committee_obj = session.query(Committee).filter_by(
                committee_code=committee_code).first()

            if committee_obj is None:
                logging.error(f"No Committee found for code: {committee_code}")
                continue  # Skip to the next iteration

            for subcommittee in committee.xpath('subcommittees/item'):
                subcommittee_code = get_text(subcommittee, 'systemCode')
                # Check if the subcommittee already exists
                existing_subcommittee = session.query(Subcommittee).filter_by(
                    subcommittee_code=subcommittee_code).first()
                if not existing_subcommittee:
                    subcommittee_activity_name = get_text(
                        subcommittee, 'activities/item/name')
                    subcommittee_activity_date_str = get_text(
                        subcommittee, 'activities/item/date')
                    subcommittee_activity_date = parse_date(
                        subcommittee_activity_date_str) if subcommittee_activity_date_str else None

                    subcommittee_obj = Subcommittee(
                        name=get_text(subcommittee, 'name'),
                        subcommittee_code=subcommittee_code,
                        activity_name=subcommittee_activity_name,
                        activity_date=subcommittee_activity_date,
                        committee_id=committee_obj.id  # Set the foreign key to link to the committee
                    )
                    subcommittees.append(subcommittee_obj)
                    # Add subcommittee object to session
                    session.add(subcommittee_obj)
    except Exception as e:
        logging.error(
            f"AttributeError in parse_subcommittees: {e}\n{traceback.format_exc()}")
        session.rollback()
        raise
    return subcommittees


def parse_cosponsors(session, bill_details, bill_id):
    """Function to parse cosponsor details and return a list of CoSponsor objects."""
    cosponsors = []
    try:
        for cosponsor in bill_details.xpath('cosponsors/item'):
            bioguide_id = get_text(cosponsor, 'bioguideId')

            # Get or create the Politician object based on the bioguide_id
            politician = get_or_create_politician(
                session, bioguide_id, cosponsor)

            cosponsor_obj = CoSponsor(
                politician_id=politician.id,  # Set the politician_id on the CoSponsor object
                sponsorship_date=parse_date(
                    get_text(cosponsor, 'sponsorshipDate')),
                is_original_cosponsor=get_text(
                    cosponsor, 'isOriginalCosponsor') == 'true',
                sponsorship_withdrawn_date=parse_date(
                    get_text(cosponsor, 'sponsorshipWithdrawnDate')),
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
        politician = session.query(Politician).filter_by(
            bioguide_id=bioguide_id).first()
        if not politician:
            first_name = get_text(cosponsor_details, 'firstName')
            last_name = get_text(cosponsor_details, 'lastName')

            if first_name:
                first_name = first_name.capitalize()

            if last_name:
                last_name = last_name.capitalize()

            politician = Politician(
                bioguide_id=bioguide_id,
                name=get_text(cosponsor_details, 'fullName'),
                first_name=first_name,
                last_name=last_name,
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
                law_obj = Law(type=law_type, number=law_number,
                              bill_id=bill_id)
                laws.append(law_obj)
    except Exception as e:
        logging.error(f"Error in parse_laws: {e}")
        # Optionally re-raise the exception
        raise
    return laws


def determine_chamber(action_text):
    if re.search(r'\bsenate\b', action_text, re.IGNORECASE):
        return "Senate"
    elif re.search(r'\bhouse\b', action_text, re.IGNORECASE):
        return "House"
    else:
        return "Unknown"


def parse_loc_summaries(session, bill_details, bill_id):
    logging.info("Entering parse_loc_summaries function")
    logging.info(f"Bill ID before creating LOCSummary: {bill_id}")

    # Query all existing LOCSummaryCodes and store them in a dictionary
    existing_codes = {
        code.version_code: code for code in session.query(LOCSummaryCode).all()}

    try:
        with session.no_autoflush:
            for summary in bill_details.xpath('summaries/summary'):
                version_code = get_text(summary, 'versionCode')
                action_date = get_text(summary, 'actionDate')
                action_desc = get_text(summary, 'actionDesc')
                update_date = get_text(summary, 'updateDate')
                text = get_text(summary, 'text')

                logging.info(
                    f"Processing summary with version code: {version_code}")

                # Convert action_date and update_date to datetime objects
                action_date = datetime.strptime(
                    action_date, '%Y-%m-%d') if action_date else None
                update_date = datetime.fromisoformat(
                    update_date.rstrip("Z")) if update_date else None

                # Get chamber and action description from version code mapping
                action_desc = version_code_mapping.get(
                    version_code, {}).get('action_desc', action_desc)

                action_text = get_text(bill_details, 'actions/item/text')
                logging.info(f"Action text: {action_text}")
                chamber_from_action_text = determine_chamber(action_text)

                # Check if a LOCSummaryCode with the extracted version_code already exists in the database
                loc_summary_code = existing_codes.get(version_code)

                # If not, create a new LOCSummaryCode object and add it to the session
                if not loc_summary_code:
                    loc_summary_code = LOCSummaryCode(
                        version_code=version_code,
                        chamber=chamber_from_action_text,
                        action_desc=action_desc
                    )
                    session.add(loc_summary_code)
                    logging.info(
                        "Created new LOCSummaryCode object and added to session")

                # Create a new LOCSummary record for each version
                logging.info(
                    f"Creating LOCSummary object with bill_id: {bill_id}")
                loc_summary = LOCSummary(
                    version_code=version_code,
                    action_date=action_date,
                    update_date=update_date,
                    action_desc=action_desc,
                    text=text,
                    loc_summary_codes=[loc_summary_code],
                    bill_id=bill_id
                )
                logging.info(
                    f"Created new LOCSummary object: {loc_summary.to_dict()}")
                session.add(loc_summary)
                session.flush()
                logging.info(
                    f"Created new LOCSummary: {loc_summary.to_dict()}")

    except Exception as e:
        logging.error(f"Error in parse_loc_summaries: {e}")
        session.rollback()  # Explicit rollback in case of error
        raise

    logging.info("Exiting parse_loc_summaries function")


def parse_notes(session, bill_details, bill_id):
    """Function to parse notes and return a list of Note objects."""
    notes = []
    try:
        for item in bill_details.xpath('notes/item'):
            note_text = get_text(item, 'text')
            bill_id = bill_id
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
        existing_policy_area = session.query(
            PolicyArea).filter_by(name=policy_area_name).first()

        if existing_policy_area:
            existing_policy_area.bill_id = bill_id
            # Assign existing policy area to the policy_area variable
            policy_area = existing_policy_area
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
            full_action_name = get_text(bill_details, 'actions/item/text')
            if roll_number and url and chamber and congress and date and session_number:
                recorded_vote_obj = RecordedVote(
                    roll_number=roll_number,
                    url=url,
                    chamber=chamber,
                    congress=congress,
                    date=date,
                    session_number=session_number,
                    bill_id=bill_id,
                    full_action_name=full_action_name
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
            # Parse attributes for the RelatedBill object
            title = get_text(related_bill, 'title')
            congress = get_text(related_bill, 'congress')
            number = get_text(related_bill, 'number')
            type = get_text(related_bill, 'type')
            action_date = parse_date(
                get_text(related_bill, 'latestAction/actionDate'))
            action_text = get_text(related_bill, 'latestAction/text')

            # Create the RelatedBill object
            related_bill_obj = RelatedBill(
                bill_id=bill_id,
                title=title,
                congress=congress,
                number=number,
                type=type,
                action_date=action_date,
                action_text=action_text,
            )

            # Parse relationship details and create BillRelationship objects
            for relationship_detail in related_bill.xpath('relationshipDetails/item'):
                relationship_type = get_text(relationship_detail, 'type')
                identified_by = get_text(relationship_detail, 'identifiedBy')
                relationship_obj = BillRelationship(
                    type=relationship_type,
                    identified_by=identified_by,
                )
                related_bill_obj.relationship_details.append(relationship_obj)

            related_bills.append(related_bill_obj)
    except Exception as e:
        logging.error(f"Error in parse_related_bills: {e}", exc_info=True)
        raise
    return related_bills


def parse_subjects(session, bill_details):
    subjects = []
    try:
        for item in bill_details.xpath('subjects/legislativeSubjects/item'):
            subject_name = get_text(item, 'name')

            # Check if a subject with the extracted name already exists in the database
            subject = session.query(Subject).filter_by(
                name=subject_name).first()

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
