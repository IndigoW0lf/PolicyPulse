import os
import requests
import time
from lxml import etree
from backend import create_app
from dotenv import load_dotenv
from api.rate_limiter import api_state, logging
from backend import db
from backend.database.models.action import Action
from backend.database.models.amendment import Amendment
from backend.database.models.bill import Bill
from backend.database.models.committee import Committee
from backend.database.models.politician import Politician
from backend.database.models.bill_full_text import BillFullText

# Load environment variables from .env file
load_dotenv()

# Set up global variables with default values from environment variables
API_KEY = os.environ.get('API_KEY')
API_BASE_URL = os.environ.get('API_BASE_URL', "https://api.congress.gov/")
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))
LIMIT = int(os.environ.get('LIMIT', 250))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
BATCH_SIZE = int(os.environ.get('BATCH_SIZE', 50))
COMMIT_THRESHOLD = int(os.environ.get('COMMIT_THRESHOLD', 500))
MODE = os.environ.get('MODE', 'populate')
DELAY_TIME_POPULATE = float(os.environ.get('DELAY_TIME_POPULATE', 3.6))
DELAY_TIME_MAINTAIN = float(os.environ.get('DELAY_TIME_MAINTAIN', 300))

# Function to manage API state and database transactions
def manage_api_state(batch_size):
    if api_state is None:
        return False  # Indicates that no commit is needed

    api_state.total_requests += 1
    api_state.batch_counter += 1
    api_state.total_items_saved += 1

    # Check if a commit is needed based on batch size
    if api_state.batch_counter >= batch_size:
        try:
            db.session.commit()
            logging.info("Database commit successful.")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Database commit failed: {e}")
        api_state.batch_counter = 0  # Reset the counter
        return True  # Indicates that a commit is needed

    return False  # Indicates that no commit is needed

# Set up headers for API requests
HEADERS = {
    "X-API-Key": API_KEY,
    "Accept": "application/json"
}

# Function to make API requests with error handling and rate limit management
def make_request(endpoint, params={}, response_format='application/json'):

    HEADERS = {
        "X-API-Key": API_KEY,
        "Accept": response_format
    }

    if api_state:
        api_state.check_and_reset_rate_limit()
    
    offset = 0  
    all_data = []

    while True:
        params.update({"limit": LIMIT, "offset": offset})
        
        for retry in range(MAX_RETRIES):
            try:
                logging.debug(f"Making request to endpoint: {endpoint}, params: {params}")
                response = requests.get(f"{API_BASE_URL}{endpoint}", headers=HEADERS, params=params)
                logging.debug(f"Response status code: {response.status_code}")
                if response.status_code >= 400:
                    logging.error(f"Received {response.status_code} error for endpoint {endpoint}.")
                    return all_data
                response.raise_for_status()
                data = response.json()

                if 'results' in data:
                    all_data.extend(data['results'])

                    if len(data['results']) < LIMIT:
                        return all_data

                    offset += LIMIT
                    time.sleep(5)

                            
                else:
                    logging.error("No 'results' key present in the data.")
                    return all_data

                break  # Successfully fetched data, so exit the retry loop
                
            except requests.RequestException as e:
                logging.error(f"Error fetching data from {endpoint}: {e}. Retrying {retry+1}/{MAX_RETRIES}.")
                time.sleep(2)  # Introducing a small delay before retrying

        else:
            logging.error(f"Reached maximum retries ({MAX_RETRIES}) for endpoint {endpoint}. Moving on.")
            return all_data

# Function to create a Bill object from API data
def create_bill(item):
    sponsor_id = fetch_sponsor_id(item.get('sponsor', ''))
    return Bill(
        title=item.get('title', ''),
        summary=item.get('summary', ''),
        bill_number=item.get('billNumber', ''),
        sponsor_name=item.get('sponsor', ''),
        sponsor_id=sponsor_id,
        date_introduced=item.get('introducedDate', None),
        status=item.get('status', ''),
        committee=",".join(item.get('committees', [])),
        full_text_link=item.get('textUrl', ''),
        tags=",".join(item.get('subjects', [])),
        last_action_date=item.get('latestActionDate', None),
        last_action_description=item.get('latestAction', ''),
    )
# NEW SECTION FOR GETTING FULL BILL DETAILS IN NESTED API CALLS
# Function to fetch bill data from API
def fetch_xml_data(xml_url, bill_id):
    response = requests.get(xml_url)
    if response.status_code == 200:
        xml_data = response.content  # This will be the XML data as bytes
        # Now you can parse the XML data as needed
        root = etree.fromstring(xml_data)
        
        # Extract metadata
        metadata = root.find('metadata/dublinCore', namespaces={'dc': 'http://purl.org/dc/elements/1.1/'})
        metadata_dict = {}
        if metadata:
            title = metadata.find('dc:title', namespaces={'dc': 'http://purl.org/dc/elements/1.1/'})
            metadata_dict['title'] = title.text if title is not None else 'N/A'

        # Extract actions
        actions_list = []
        actions = root.findall('form/action', namespaces={})
        for action in actions:
            action_date = action.find('action-date')
            action_desc = action.find('action-desc')
            actions_list.append({
                "action_date": action_date.get('date') if action_date is not None else 'N/A',
                "action_description": etree.tostring(action_desc).decode('utf-8') if action_desc is not None else 'N/A'
            })

        # Extract bill details
        sections_list = []
        legis_body = root.find('legis-body', namespaces={})
        if legis_body:
            sections = legis_body.findall('section', namespaces={})
            for section in sections:
                header = section.find('header')
                text = section.find('text')
                sections_list.append({
                    "section_header": header.text if header is not None else 'N/A',
                    "section_text": etree.tostring(text).decode('utf-8') if text is not None else 'N/A'
                })

        # Create a new BillFullText object and store the parsed data
        bill_full_text = BillFullText(
            bill_id=bill_id,
            title=metadata_dict.get('title'),
            metadata=metadata_dict,
            actions=actions_list,
            sections=sections_list
        )
        
        # Add the new BillFullText object to the session
        db.session.add(bill_full_text)

        # Commit the session to save the BillFullText object to the database
        try:
            db.session.commit()
            logging.info(f"Successfully stored full text for bill ID {bill_id} in the database.")
        except Exception as e:
            db.session.rollback()
            logging.error(f"An error occurred while saving to database: {e}")

        return xml_data  # You might want to return parsed data instead of raw XML
    else:
        logging.error(f"Failed to fetch XML data from {xml_url}. Status code: {response.status_code}")
        return None


def fetch_full_bill_text(url):
    response = requests.get(url, headers={"Accept": "application/xml"})
    if response.status_code == 200:
        return response.text  # This will return the XML as a string
    else:
        logging.error(f"Failed to fetch full bill details from {url}. Status code: {response.status_code}")
        return None
# END NEW SECTION FOR GETTING FULL BILL DETAILS IN NESTED API CALLS


def fetch_bill_actions(bill_id):
    manage_api_state(api_state, 1)
    endpoint = f"v3/bill/{bill_id}/actions"
    logging.debug(f"Fetching actions for bill_id: {bill_id}")
    return make_request(endpoint, api_state=api_state)

def fetch_bill_amendments(bill_id):
    manage_api_state(api_state, 1)
    endpoint = f"v3/bill/{bill_id}/amendments"
    logging.debug(f"Fetching amendments for bill_id: {bill_id}")
    return make_request(endpoint, api_state=api_state)

def fetch_bill_committees(bill_id):
    manage_api_state(api_state, 1)
    endpoint = f"v3/bill/{bill_id}/committees"
    logging.debug(f"Fetching committees for bill_id: {bill_id}")
    return make_request(endpoint, api_state=api_state)

def fetch_sponsor_id(sponsor_name):
    sponsor = Politician.query.filter_by(name=sponsor_name).first()
    return sponsor.id if sponsor else None

# Function to store actions related to a bill in the database
def store_actions(bill, bill_id):
    actions = fetch_bill_actions(bill_id)
    if actions:
        for action in actions:
            action_record = Action(
                action_date=action.get('date', None),
                description=action.get('description', ''),
                chamber=action.get('chamber', ''),
                bill_id=bill.id
            )
            db.session.add(action_record)

# Store related amendments for a bill
def store_amendments(bill, bill_id):
    amendments = fetch_bill_amendments(bill_id)
    if amendments:
        for amendment in amendments:
            amendment_record = Amendment(
                amendment_number=amendment.get('number', ''),
                description=amendment.get('description', ''),
                date_proposed=amendment.get('proposedDate', None),
                status=amendment.get('status', ''),
                bill_id=bill.id
            )
            db.session.add(amendment_record)

# Store related committees for a bill
def store_committees(bill, bill_id):
    committees = fetch_bill_committees(bill_id)
    if committees:
        for committee in committees:
            committee_record = Committee(
                name=committee.get('name', ''),
                chamber=committee.get('chamber', ''),
                committee_code=committee.get('systemCode', ''),
            )
            db.session.add(committee_record)

# Store a bill and its related records, manage API state and transactions
processed_bill_ids = set()

# Function to process and store bill data in the database
def store_bill(data, batch_size=50):
    if not data:
        logging.error("No data to process.")
        return

    batch = []
    for item in data:
        bill_id = item.get('bill_id')
        
        if not bill_id:
            logging.error("bill_id is missing in the data.")
            continue

        if bill_id in processed_bill_ids:
            continue

        bill = create_bill(item)
        db.session.add(bill)

        # Store related records
        store_actions(bill, bill_id)
        store_amendments(bill, bill_id)
        store_committees(bill, bill_id)

        batch.append(item)

        # Manage API state and transactions
        commit_needed = manage_api_state(api_state, batch_size)
        
        if commit_needed:
            try:
                db.session.commit()
                logging.info(f"Successfully stored {batch_size} bills in the database.")
                processed_bill_ids.update([x.get('bill_id') for x in batch])
                batch.clear()
            except Exception as e:
                db.session.rollback()
                logging.error(f"An error occurred while saving to database: {e}")

    # Commit any remaining items (if any)
    if batch:
        try:
            db.session.commit()
            logging.info(f"Successfully stored {len(batch)} bills in the database.")
            processed_bill_ids.update([x.get('bill_id') for x in batch])
        except Exception as e:
            db.session.rollback()
            logging.error(f"An error occurred while saving to database: {e}")

# Function to get summary data for a specific bill
def get_bill_summary(congress, bill_type):
    if api_state:
        api_state.check_and_reset_rate_limit()

    # Create the API endpoint for this specific bill summary
    endpoint = f"v3/summaries/{congress}/{bill_type}"

    # Make a request to fetch the summary data
    summary_data = make_request(endpoint, api_state=api_state)

    return summary_data

def get_committee_details(congress, chamber, batch_size=100):
    manage_api_state(api_state, batch_size)
    
    endpoint = f"v3/committee/{congress}/{chamber}"
    response = make_request(endpoint, api_state=api_state)
    
    if response is not None:
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get details for {congress} {chamber}. Status code: {response.status_code}")
            return None
    else:
        logging.error("No response received.")
        return None

# Main function to orchestrate data fetching and storing
def main():
    offset = 0
    while True:
        bills_data = fetch_bills(offset=offset, limit=LIMIT)
        if not bills_data or not bills_data.get('bills'):
            break

        for bill_data in bills_data['bills']:
            bill_url = bill_data.get('url')
            if bill_url:
                full_bill_text = fetch_full_bill_text(bill_url)
                if full_bill_text:
                    # Parse the full bill text to extract relevant information
                    # (this depends on the structure of the full bill text JSON)
                    parsed_data = parse_full_bill_text(full_bill_text)

                    # Create a new Bill object and set its attributes based on the parsed data
                    bill = Bill(
                        title=parsed_data.get('title', ''),
                        summary=parsed_data.get('summary', ''),
                        # ... (set other attributes as needed)
                    )

                    # Add the new Bill object to the session
                    db.session.add(bill)

                    # Commit the session to save the Bill object to the database
                    try:
                        db.session.commit()
                        logging.info(f"Successfully stored bill {bill.title} in the database.")
                    except Exception as e:
                        db.session.rollback()
                        logging.error(f"An error occurred while saving to database: {e}")

        offset += LIMIT


def parse_full_bill_text(full_bill_details):
    # This function should parse the full bill details JSON to extract the relevant information
    # The exact implementation depends on the structure of the full bill details JSON
    # Here's a placeholder implementation that just returns the full bill details JSON as is
    
    bill_text_url = full_bill_details.get('bill', {}).get('textVersions', {}).get('url')
    if bill_text_url:
        response = requests.get(bill_text_url)
        if response.status_code == 200:
            bill_text = response.json()
            # Now bill_text should contain the full text of the bill
            # You would need to extract the relevant information from bill_text and return it
            # The exact implementation depends on the structure of the bill_text JSON
            return bill_text
        else:
            logging.error(f"Failed to fetch full bill text from {bill_text_url}. Status code: {response.status_code}")
            return None
    else:
        logging.error("No URL found to fetch the full bill text.")
        return None

# Function to run the script in different modes (populate or maintain)s
def run_script():
    first_run = True  # Set this to False once the initial population is done

    if first_run:
        logging.info("Populating database...")
        main('populate')
    else:
        logging.info("Maintaining database...")
        main('maintain')

if __name__ == "__main__":
    app = create_app()  # Create the app instance
    with app.app_context():
        main()