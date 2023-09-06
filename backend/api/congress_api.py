import os
import requests
import time
from lxml import etree
from backend import create_app
from dotenv import load_dotenv
from .rate_limiter import api_state, logging
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
def manage_api_state(api_state, batch_size):
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
def make_request(endpoint, api_state, params={}, response_format='application/json'):

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
        bill_number=item.get('bill_number', ''),
        sponsor_name=item.get('sponsor', ''),
        sponsor_id=sponsor_id,
        date_introduced=item.get('date_introduced', None),
        status=item.get('status', ''),
        committee=",".join(item.get('committees', [])),
        full_bill_link=item.get('full_bill_link', ''),
        tags=",".join(item.get('subjects', [])),
        last_action_date=item.get('last_action_date', None),
        last_action_description=item.get('last_action_description', ''),
    )
# Step 1 nested function to get XML data
def fetch_list_of_bills():
    response = requests.get(f"{API_BASE_URL}v3/bill?limit={LIMIT}&format=json")
    if response.status_code == 200:
        data = response.json()
        if data.get('bills') and len(data['bills']) > 0:
            bill_url = data['bills'][0]['url']
            return bill_url
        else:
            print('No bills found or invalid response structure')
            return None
    else:
        print(f"Failed to fetch list of bills. Status code: {response.status_code}")
        return None
    
# Step 2 nested function to get XML data    
def fetch_individual_bill_details(bill_url):
    response = requests.get(bill_url)
    if response.status_code == 200:
        bill_details = response.json()
        # Here you can add code to parse the JSON data and extract the information you need
        # ...
        return bill_details
    else:
        print(f"Failed to fetch individual bill details from {bill_url}. Status code: {response.status_code}")
        return None

# Step 3 nested function to get XML data   
def fetch_text_versions_of_bill(text_versions_url):
    response = requests.get(text_versions_url)
    if response.status_code == 200:
        data = response.json()
        if data.get('textVersions') and len(data['textVersions']) > 0:
            formatted_xml_version = next((format for format in data['textVersions'][0]['formats'] if format['type'] == 'Formatted XML'), None)
            if formatted_xml_version:
                xml_url = formatted_xml_version['url']
                return xml_url
            else:
                print('No Formatted XML version found')
                return None
        else:
            print('No text versions found or invalid response structure')
            return None
    else:
        print(f"Failed to fetch text versions of bill from {text_versions_url}. Status code: {response.status_code}")
        return None

# Step 4 nested function to get XML data
def fetch_individual_text_version(xml_url):
    response = requests.get(xml_url)
    if response.status_code == 200:
        xml_data = response.content
        tree = etree.fromstring(xml_data)
        
        # Parse the XML data and extract relevant information
        namespace_map = {'dc': 'http://purl.org/dc/elements/1.1/'}
        bill_metadata = tree.find('metadata')
        if bill_metadata is not None:
            dublin_core = bill_metadata.find('dublinCore')
            if dublin_core is not None:
                title = dublin_core.find('dc:title', namespaces=namespace_map).text
                publisher = dublin_core.find('dc:publisher', namespaces=namespace_map).text
                date = dublin_core.find('dc:date', namespaces=namespace_map).text
                format = dublin_core.find('dc:format', namespaces=namespace_map).text
                language = dublin_core.find('dc:language', namespaces=namespace_map).text
                rights = dublin_core.find('dc:rights', namespaces=namespace_map).text

                parsed_data = {
                    "title": title,
                    "publisher": publisher,
                    "date": date,
                    "format": format,
                    "language": language,
                    "rights": rights
                }

                return parsed_data
            else:
                print("Dublin Core not found in the XML data")
        else:
            print("Metadata not found in the XML data")
    else:
        print(f"Failed to fetch individual text version from {xml_url}. Status code: {response.status_code}")

def store_full_bill_text(bill, xml_url):
    # Get the parsed data from the fetch_individual_text_version function
    xml_data = fetch_individual_text_version(xml_url)
    
    if xml_data:
        # Create a BillFullText record
        bill_full_text_record = BillFullText(
            bill_id=bill.id,
            title=xml_data.get('title'),
            bill_metadata=xml_data,  # Storing the parsed metadata
        )
        
        db.session.add(bill_full_text_record)

        # Print the new object to check if it's created correctly
        print(bill_full_text_record)

    # Commit the transaction
    db.session.commit()

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
    
def fetch_bills(offset=0, limit=50):
    # This function should fetch a list of bills and their details
    # The exact implementation depends on the API endpoints and parameters
    # Here's a placeholder implementation:

    bills_data = []
    for i in range(offset, offset+limit):
        bill_url = fetch_list_of_bills()  # Step 1: Get list of bills
        if bill_url:
            bill_details = fetch_individual_bill_details(bill_url)  # Step 2: Get individual bill details
            if bill_details:
                text_versions_url = bill_details.get('textVersions', {}).get('url')
                if text_versions_url:
                    xml_url = fetch_text_versions_of_bill(text_versions_url)  # Step 3: Get text versions of bill
                    if xml_url:
                        xml_data = fetch_individual_text_version(xml_url)  # Step 4: Get individual text version
                        if xml_data:
                            bill_details['full_text'] = xml_data
                            bills_data.append(bill_details)
    return {'bills': bills_data}


# Store a bill and its related records, manage API state and transactions
processed_bill_ids = set()

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

        # Fetch and store full bill text
        bill_url = fetch_list_of_bills()
        if bill_url:
            bill_details = fetch_individual_bill_details(bill_url)
            if bill_details:
                text_versions_url = bill_details.get('textVersionsUrl')
                if text_versions_url:
                    xml_url = fetch_text_versions_of_bill(text_versions_url)
                    if xml_url:
                        xml_data = fetch_individual_text_version(xml_url)
                        if xml_data:
                            store_full_bill_text(bill, xml_data)

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

# Main function to orchestrate data fetching and storing
def main(mode='populate'):
    offset = 0
    while True:
        bills_data = fetch_bills(offset=offset, limit=LIMIT)
        if not bills_data or not bills_data.get('bills'):
            break

        # Call store_bill function to store the bill data
        store_bill(bills_data['bills'])

        offset += LIMIT

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
        run_script()
