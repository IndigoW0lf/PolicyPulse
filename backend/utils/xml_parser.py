import logging
import os
from backend import db
from backend.database.models import (Bill, Action, Amendment, BillFullText, Committee, CoSponsor, LOCSummary, Politician,PolicyArea, RelatedBill, Subject, VetoMessage)
from backend.utils.keywords import keywords
from dotenv import load_dotenv
from lxml import etree
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env file
load_dotenv()

# Get the XML files directory from environment variables
XML_FILES_DIRECTORY = os.getenv('XML_FILES_DIRECTORY')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BATCH_SIZE = 100  # Adjust the batch size as needed

def parse_xml_files(directory, keywords, save_function):
    print(f"Directory: {directory}, Keywords: {keywords}")
    xml_files = [f for f in os.listdir(directory) if f.endswith('.xml')]
    batch_counter = 0

    for xml_file in xml_files:
        try:
            tree = etree.parse(os.path.join(directory, xml_file))
            
            # Extracting the title and summary text
            title_element = tree.find(".//bill/title") or tree.find(".//bill/titles/item/title")
            summary_element = tree.find(".//bill/summaries/summary/text")
            
            if title_element is not None and summary_element is not None:
                title_text = title_element.text
                summary_text = summary_element.text
                
                logging.info("XML in Files: %s", xml_files)
                logging.info("Title Text: %s", title_text)
                logging.info("Summary Text: %s", summary_text)

                if any(keyword.lower() in (title_text + summary_text).lower() for keyword in keywords):
                    logging.info(f"Keyword found in file: {xml_file}")
                    bill_data = parse_bill(tree)
                    save_function(bill_data)
                else:
                    logging.info(f"No keywords found in file: {xml_file}")
            else:
                logging.warning(f"Title or summary not found in file: {xml_file}")

            batch_counter += 1
            if batch_counter % BATCH_SIZE == 0:
                db.session.commit()
                batch_counter = 0      

        except Exception as e:
            logging.error(f"Error processing file {xml_file}: {e}", exc_info=True)
            db.session.rollback()
        
    # Commit any remaining transactions
    if batch_counter > 0:
        db.session.commit()

def parse_bill(tree):
    # Parse the bill data from the XML tree.
    bill_data = {
        'number': get_text(tree, './/bill/number'),
        'updateDate': get_text(tree, './/bill/updateDate'),
        'originChamber': get_text(tree, './/bill/originChamber'),
        'type': get_text(tree, './/bill/type'),
        'introducedDate': get_text(tree, './/bill/introducedDate'),
        'congress': get_text(tree, './/bill/congress'),
        'display_title': get_display_title(tree),
        'official_title': get_official_title(tree),
        'sponsor': parse_sponsor(tree),
        'summaries': parse_summaries(tree),
        'fullBillTexts': parse_fullBillTexts(tree),
        'subjects': parse_subjects(tree),
        "textVersions": parse_text_versions(tree),
        "latestAction": parse_latest_action(tree),
        "titles": parse_titles(tree),
        "committees": parse_committees(tree),
        "sponsors": parse_sponsors(tree),
        "vetoMessages": parse_veto_messages(tree),
        "policyAreas": parse_policyAreas(tree),
        "relatedBills": parse_relatedBills(tree),
        "coSponsors": parse_coSponsors(tree),
        "fullBillTexts": parse_fullBillTexts(tree),
        "actions": parse_actions(tree),
        "amendments": parse_amendments(tree),
    }
    return bill_data

def get_text(tree, xpath):
    elements = tree.xpath(xpath)
    if elements:
        if len(elements) == 1:
            return elements[0].text
        else:
            return [element.text for element in elements]
    else:
        return None

def get_or_create_politician(sponsor_name, sponsor_state):
    politician = Politician.query.filter_by(name=sponsor_name, state=sponsor_state).first()
    if not politician:
        politician = Politician(name=sponsor_name, state=sponsor_state)
        db.session.add(politician)
        db.session.commit()
    return politician

def get_display_title(tree):
    title_element = tree.find(".//bill/titles/item[titleType='Display Title']")
    return title_element.text if title_element is not None else ""

def get_official_title(tree):
    title_element = tree.find(".//bill/titles/item[titleType='Official Title as Introduced']")
    return title_element.text if title_element is not None else ""

def get_text(element, tag):
    """Helper function to get the text of a child element with the given tag."""
    child = element.find(tag)
    return child.text if child is not None else None

def parse_actions(tree):
    """Parse the actions section of the bill data."""
    actions = tree.findall(".//bill/actions/item")
    return [
        {
            "actionDate": get_text(action, "actionDate"),
            "actionTime": get_text(action, "actionTime"),
            "committee": {
                "name": get_text(action, "committee/name"),
            },
            "text": get_text(action, "text"),
            "type": get_text(action, "type"),
            "actionCode": get_text(action, "actionCode"),
            "sourceSystem": {
                "code": get_text(action, "sourceSystem/code"),
                "name": get_text(action, "sourceSystem/name"),
            }
        }
        for action in actions
    ]

def parse_amendments(tree):
    """Parse the amendments section of the bill data."""
    amendments = tree.findall(".//bill/amendments/item")
    return [
        {
            "amendment_number": get_text(amendment, "amendment_number"),
            "description": get_text(amendment, "description"),
            "date_proposed": get_text(amendment, "date_proposed"),
            "status": get_text(amendment, "status"),
        }
        for amendment in amendments
    ]

def parse_committees(tree):
    """Parse the committees section of the bill data."""
    committees = tree.findall(".//bill/committees/item")
    return [
        {
            "name": get_text(committee, "name"),
            "chamber": get_text(committee, "chamber"),
            "committee_code": get_text(committee, "committee_code"),
        }
        for committee in committees
    ]

def parse_coSponsors(tree):
    """Parse the co-sponsors section of the bill data."""
    co_sponsors = tree.findall(".//bill/coSponsors/item")
    return [
        {
            "politician_id": get_text(co_sponsor, "politician_id"),
            "bill_id": get_text(co_sponsor, "bill_id"),
        }
        for co_sponsor in co_sponsors
    ]

def parse_fullBillTexts(tree):
    """Parse the full bill texts section of the bill data."""
    full_bill_texts = tree.findall(".//bill/fullBillTexts/item")
    return [
        {
            "title": get_text(full_bill_text, "title"),
            "bill_metadata": get_text(full_bill_text, "bill_metadata"),
            "actions": get_text(full_bill_text, "actions"),
            "sections": get_text(full_bill_text, "sections"),
        }
        for full_bill_text in full_bill_texts
    ]

def parse_latest_action(tree):
    """Parse the latest action section of the bill data."""
    return {
        "actionDate": get_text(tree, ".//bill/latestAction/actionDate"),
        "text": get_text(tree, ".//bill/latestAction/text"),
        "actionTime": get_text(tree, ".//bill/latestAction/actionTime"),
    }

def parse_policyAreas(tree):
    """Parse the policy areas section of the bill data."""
    policy_areas = tree.findall(".//bill/policyAreas/item")
    return [
        {
            "name": get_text(policy_area, "name"),
            "description": get_text(policy_area, "description"),
        }
        for policy_area in policy_areas
    ]

def parse_relatedBills(tree):
    """Parse the related bills section of the bill data."""
    related_bills = tree.findall(".//bill/relatedBills/item")
    return [
        {
            "bill_id": get_text(related_bill, "bill_id"),
            "related_bill_id": get_text(related_bill, "related_bill_id"),
        }
        for related_bill in related_bills
    ]

def parse_sponsors(tree):
    """Parse the sponsors and cosponsors section of the bill data."""
    sponsors = tree.findall(".//bill/sponsors/item") + tree.findall(".//bill/cosponsors/item")
    return [
        {
            "bioguide_id": get_text(sponsor, "bioguideId"),
            "first_name": get_text(sponsor, "firstName"),
            "middle_name": get_text(sponsor, "middleName"),
            "last_name": get_text(sponsor, "lastName"),
            "name": " ".join(filter(None, [get_text(sponsor, "firstName"), get_text(sponsor, "middleName"), get_text(sponsor, "lastName")])),  # Combining first, middle and last names
            "party": get_text(sponsor, "party"),
            "state": get_text(sponsor, "state"),
        }
        for sponsor in sponsors
    ]


def parse_subjects(tree):
    """Parse the subjects section of the bill data."""
    return {
        'legislativeSubjects': [
            {'name': get_text(subject, 'name')}
            for subject in tree.xpath('.//bill/subjects/legislativeSubjects/item')
        ],
        'billSubjects': [
            {'name': get_text(subject, 'name')}
            for subject in tree.xpath('.//bill/subjects/billSubjects/item')
        ],
        'otherSubjects': [
            {
                'name': get_text(subject, 'name'),
                'parentSubject': {'name': get_text(subject, 'parentSubject/name')}
            }
            for subject in tree.xpath('.//bill/subjects/otherSubjects/item')
        ],
        'primarySubjects': [
            {
                'name': get_text(subject, 'name'),
                'parentSubject': {'name': get_text(subject, 'parentSubject/name')}
            }
            for subject in tree.xpath('.//bill/subjects/primarySubjects/item')
        ]
    }

def parse_summaries(tree):
    """Parse the summaries section of the bill data."""
    summaries = tree.findall(".//bill/summaries/summary")
    versions = [
        {
            "version_code": get_text(summary, "versionCode"),
            "action_date": get_text(summary, "actionDate"),
            "action_desc": get_text(summary, "actionDesc"),
            "update_date": get_text(summary, "updateDate"),
            "text": get_text(summary, "text"),
        }
        for summary in summaries
    ]
    return {"versions": versions}


def parse_titles(tree):
    """Parse the titles section of the bill data."""
    titles = tree.findall(".//bill/titles/item")
    for title in titles:
        title_type = get_text(title, "titleType")
        if title_type == "Official Title as Introduced":
            return get_text(title, "title")
    return ""  # Return an empty string if no matching title is found

def parse_text_versions(tree):
    """Parse the text versions section of the bill data."""
    text_versions = tree.findall(".//bill/textVersions/item")
    return [
        {
            "type": get_text(version, "type"),
            "date": get_text(version, "date"),
            "url": get_text(version, "formats/item/url"),
        }
        for version in text_versions
    ]

def parse_veto_messages(tree):
    """Parse the veto messages section of the bill data."""
    veto_messages = tree.findall(".//bill/vetoMessages/item")
    return [
        {
            "date": get_text(veto_message, "date"),
            "message": get_text(veto_message, "message"),
            "president": get_text(veto_message, "president"),
            "text": get_text(veto_message, "text"),
        }
        for veto_message in veto_messages
    ]

def save_to_database(bill_data):
    try:
        # Step 1: Create or find existing records for related models
        sponsor_data = bill_data.get('sponsor', {})
        sponsor_name = sponsor_data.get('name')
        sponsor_state = sponsor_data.get('state')
        if sponsor_name and sponsor_state:
            sponsor = get_or_create_politician(sponsor_name, sponsor_state)
        else:
            sponsor = None

        # Step 2: Create a new Bill instance
        bill = Bill(
            number=bill_data['number'],
            update_date=bill_data['update_date'],
            origin_chamber=bill_data['origin_chamber'],
            bill_type=bill_data['bill_type'],
            introduced_date=bill_data['introduced_date'],
            congress=bill_data['congress'],
            display_title=bill_data['display_title'],
            official_title=bill_data['official_title'],
            sponsor_id=sponsor.id,
        )
        db.session.add(bill)

        # Step 3: Create new instances for other related models and link them to the Bill instance
        for action_data in bill_data['actions']:
            action = Action(
                action_date=action_data['action_date'],
                text=action_data['text'],
                type=action_data['type'],
                action_code=action_data['action_code'],
                source_system_code=action_data['source_system']['code'],
                source_system_name=action_data['source_system']['name'],
                bill_id=bill.id,
            )
            db.session.add(action)

        # Save amendments
        for amendment_data in bill_data['amendments']:
            amendment = Amendment(
                amendment_number=amendment_data['amendment_number'],
                description=amendment_data['description'],
                date_proposed=amendment_data['date_proposed'],
                status=amendment_data['status'],
                bill_id=bill.id,
            )
            db.session.add(amendment)

        # Save committees
        for committee_data in bill_data['committees']:
            committee = Committee(
                name=committee_data['name'],
                chamber=committee_data['chamber'],
                committee_code=committee_data['committee_code'],
                bill_id=bill.id,
            )
            db.session.add(committee)

        # Save co-sponsors
        for co_sponsor_data in bill_data['coSponsors']:
            co_sponsor = CoSponsor(
                politician_id=co_sponsor_data['politician_id'],
                bill_id=bill.id,
            )
            db.session.add(co_sponsor)

        # Save full bill texts
        for full_bill_text_data in bill_data['fullBillTexts']:
            full_bill_text = BillFullText(
                display_title=full_bill_text_data['display_title'],
                bill_metadata=full_bill_text_data['bill_metadata'],
                actions=full_bill_text_data['actions'],
                sections=full_bill_text_data['sections'],
                bill_id=bill.id,
            )
            db.session.add(full_bill_text)
        
        # Save latest action
        latest_action_data = bill_data['latestAction']
        latest_action = Action(
            action_date=latest_action_data['actionDate'],
            text=latest_action_data['text'],
            action_time=latest_action_data['actionTime'],
            bill_id=bill.id,
            is_latest=True,
        )
        db.session.add(latest_action)
        db.session.commit()
        
        # Save policy areas
        for policy_area_data in bill_data['policyAreas']:
            policy_area = PolicyArea(
                name=policy_area_data['name'],
                bill_id=bill.id,
            )
            db.session.add(policy_area)

        # Save related bills
        for related_bill_data in bill_data['relatedBills']:
            related_bill = RelatedBill(
                related_bill_id=related_bill_data['related_bill_id'],
                bill_id=bill.id,
            )
            db.session.add(related_bill)

         # Save subjects
        for subject_data in bill_data['subjects']['legislativeSubjects']:
            subject = Subject(
                name=subject_data['name'],
                bill_id=bill.id,
            )
            db.session.add(subject)

        # Save billSubjects
        for subject_data in bill_data['subjects']['billSubjects']:
            subject = Subject(
                name=subject_data['name'],
                bill_id=bill.id,
            )
            db.session.add(subject)

        # Save otherSubjects
        for subject_data in bill_data['subjects']['otherSubjects']:
            subject = Subject(
                name=subject_data['name'],
                parent_subject=subject_data['parentSubject']['name'],
                bill_id=bill.id,
            )
            db.session.add(subject)

        # Save primarySubjects
        for subject_data in bill_data['subjects']['primarySubjects']:
            subject = Subject(
                name=subject_data['name'],
                parent_subject=subject_data['parentSubject']['name'],
                bill_id=bill.id,
            )
            db.session.add(subject)

        # Save summaries
        summary_data = bill_data['summaries']
        if summary_data:
            loc_summary = LOCSummary(
                versions=summary_data['versions'],
                bill_id=bill.id,
            )
            db.session.add(loc_summary)

            
        # Save text versions
        for text_version_data in bill_data['textVersions']:
            text_version = BillFullText(
                type=text_version_data['type'],
                date=text_version_data['date'],
                url=text_version_data['url'],
                bill_id=bill.id,
            )
        db.session.add(text_version)

        #Save veto messages
        for veto_message_data in bill_data['vetoMessages']:
            veto_message = VetoMessage(
                date=veto_message_data['date'],
                message=veto_message_data['message'],
                president=veto_message_data['president'],
                text=veto_message_data['text'],
                bill_id=bill.id,
            )
            db.session.add(veto_message)
            
        db.session.commit()
    
    except SQLAlchemyError as e:
      logging.error(f"Database error: {e}", exc_info=True)
      db.session.rollback()
    except Exception as e:
      logging.error(f"Unexpected error: {e}", exc_info=True)
      db.session.rollback()

# Specify the directory containing your XML files and the keywords to search for
if __name__ == "__main__":
    parse_xml_files(XML_FILES_DIRECTORY, keywords)