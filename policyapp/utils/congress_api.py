import requests
import time
import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from policyapp.models import Bill, Action, Amendment, Committee, db  # Updated Bill to Bill
from config import API_KEY

logging.basicConfig(filename='app.log', level=logging.ERROR)

class ApiState:
    def __init__(self):
        self.total_requests = 0
        self.total_items_fetched = 0
        self.total_items_saved = 0
        self.batch_counter = 0
        self.first_request_time = None 

    def check_and_reset_rate_limit(self):
        current_time = datetime.now()
        if self.first_request_time is None:
            self.first_request_time = current_time

        if current_time - self.first_request_time >= timedelta(hours=1):
            self.total_requests = 0
            self.first_request_time = current_time

        if self.total_requests >= 1000:
            reset_time = self.first_request_time + timedelta(hours=1)
            sleep_time = (reset_time - current_time).seconds
            logging.error(f"Approaching rate limit. Pausing for {sleep_time} seconds.")
            time.sleep(sleep_time)
            self.total_requests = 0
            self.first_request_time = datetime.now()

api_state = ApiState()

def manage_api_state(api_state, batch_size, commit_threshold=500):
    if api_state is None:
        return False  # Indicates that no commit is needed

    api_state.total_requests += 1
    api_state.batch_counter += 1
    api_state.total_items_saved += 1

    # Check if a commit is needed based on batch size
    if api_state.batch_counter >= batch_size:
        api_state.batch_counter = 0  # Reset the counter
        return True  # Indicates that a commit is needed

    # Check if a commit is needed based on total items saved
    elif api_state.total_items_saved >= commit_threshold:
        api_state.total_items_saved = 0  # Reset the counter
        return True  # Indicates that a commit is needed

    return False  # Indicates that no commit is needed

API_BASE_URL = "https://api.congress.gov/"
MAX_RETRIES = 3
LIMIT = 250
HEADERS = {
    "X-API-Key": API_KEY,
    "Accept": "application/json"
}

def make_request(endpoint, params={}, api_state=None):
    offset = 0  
    all_data = []

    while True:
        params.update({"limit": LIMIT, "offset": offset})
        
        for retry in range(MAX_RETRIES):
            try:
                # Check and reset rate limit here
                api_state.check_and_reset_rate_limit()

                response = requests.get(f"{API_BASE_URL}{endpoint}", headers=HEADERS, params=params)
                response.raise_for_status()
                data = response.json()

                if 'results' in data:
                    all_data.extend(data['results'])

                    if len(data['results']) < LIMIT:
                        return all_data

                    offset += LIMIT
                    time.sleep(5)

                    if api_state is not None:
                        api_state.total_requests += 1
                            
                else:
                    logging.error("No 'results' key present in the data.")
                    return all_data

                break  # Successfully fetched data, so exit the retry loop
                
            except requests.RequestException as e:
                logging.error(f"Error fetching data from {endpoint}: {e}. Retrying {retry+1}/{MAX_RETRIES}.")
                time.sleep(2)  # Introducing a small delay

        else:
            logging.error(f"Reached maximum retries ({MAX_RETRIES}) for endpoint {endpoint}. Moving on.")
            return all_data


# Bill Endpoint
def fetch_all_bills_by_keyword(keyword):
    endpoint = "bill"
    all_data = []
    page = 1

    while True:
        data = make_request(endpoint, params={"search": keyword, "page": page}, api_state=api_state)
        if not data:
            break

        all_data.extend(data.get('bills', []))

        if "next" not in data.get('Pagination', {}):
            break

        page += 1

    return all_data

def fetch_bill_actions(bill_id, api_state=None):
    manage_api_state(api_state, 1)
    endpoint = f"bill/{bill_id}/actions"
    return make_request(endpoint, api_state=api_state)

def fetch_bill_amendments(bill_id, api_state=None):
    manage_api_state(api_state, 1)
    endpoint = f"bill/{bill_id}/amendments"
    return make_request(endpoint, api_state=api_state)

def fetch_bill_committees(bill_id, api_state=None):
    manage_api_state(api_state, 1)
    endpoint = f"bill/{bill_id}/committees"
    return make_request(endpoint, api_state=api_state)

# Create a single bill from an item dictionary
def create_bill(item):
    return Bill(
        title=item.get('title', ''),
        summary=item.get('summary', ''),
        bill_number=item.get('billNumber', ''),
        sponsor_name=item.get('sponsor', ''),
        date_introduced=item.get('introducedDate', None),
        status=item.get('status', ''),
        committee=",".join(item.get('committees', [])),
        full_text_link=item.get('textUrl', ''),
        tags=",".join(item.get('subjects', [])),
        last_action_date=item.get('latestActionDate', None),
        last_action_description=item.get('latestAction', ''),
    )

# Store related actions for a bill
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

# Store a bill and its related records, manage API state and transactions
processed_bill_ids = set()

def store_bill(data, batch_size=50, api_state=None):
    for item in data:
        bill_id = item.get('bill_id')
        
        if bill_id in processed_bill_ids:
            continue

        bill = create_bill(item)
        db.session.add(bill)

        # Store related records
        store_actions(bill, item.get('bill_id'))
        store_amendments(bill, item.get('bill_id'))
        store_committees(bill, item.get('bill_id'))

        # Manage API state and transactions
        commit_needed = manage_api_state(api_state, batch_size)
        
        if commit_needed:
            try:
                db.session.commit()
                logging.info("Database commit successful.")
                processed_bill_ids.add(bill_id)
            except Exception as e:
                db.session.rollback()
                logging.error(f"Database commit failed: {e}")

    # Commit any remaining items (if any)
    try:
        db.session.commit()
        logging.info("Database commit successful.")
        processed_bill_ids.add(bill_id)  # Add here after successful commit
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while saving to database: {e}")


def main(mode='populate'):
    if mode == 'populate':
        delay_time = 3.6  # 1000 requests/hour
    elif mode == 'maintain':
        delay_time = 300  # Run every 5 minutes when in maintenance mode
    else:
        logging.error("Invalid mode")
        return
    
    KEYWORDS = [
    "LGBTQ", "LGBT", "gay rights", "transgender rights", "bisexual", "lesbian", "gay men", "transgender people", "queer", "gender identity", "sexual orientation", "homophobia", "transphobia", "gender nonconforming", "non-binary", "genderqueer", "intersex", "same-sex marriage", "civil union", "domestic partnership", "coming out", "closeted", "top surgery", "bottom surgery", "facial feminization surgery", "sexual minorities", "gender minorities", "transitioning", "hormone therapy", 
    "gender-affirming surgery", "gender dysphoria", "two-spirit", "LGBTQ youth", 
    "LGBTQ elders", "LGBTQ health", "LGBTQ families", "LGBTQ adoption", "LGBTQ military service", 
    "LGBTQ veterans", "LGBTQ employment", "LGBTQ discrimination", "LGBTQ immigration", 
    "LGBTQ asylum seekers", "LGBTQ refugees", "LGBTQ homelessness", "LGBTQ housing", 
    "LGBTQ education", "LGBTQ students", "LGBTQ bullying", "LGBTQ suicide", "LGBTQ mental health", 
    "LGBTQ substance abuse", "LGBTQ HIV/AIDS", "LGBTQ community", "LGBTQ culture", 
    "LGBTQ history", "LGBTQ pride", "LGBTQ activism", "LGBTQ representation", "LGBTQ media", 
    "LGBTQ literature", "LGBTQ arts", "LGBTQ film", "LGBTQ television", "LGBTQ music", 
    "LGBTQ sports", "LGBTQ religion", "LGBTQ spirituality", "LGBTQ churches", "LGBTQ synagogues", 
    "LGBTQ mosques", "LGBTQ temples", "LGBTQ clergy", "LGBTQ theology", "LGBTQ religious texts", 
    "LGBTQ religious leaders", "LGBTQ saints", "LGBTQ religious history", "LGBTQ religious rites", 
    "LGBTQ religious discrimination", "LGBTQ religious acceptance", "LGBTQ religious inclusion", "trans medical care", "gender-affirming care", "trans healthcare", "trans youth healthcare",
    "puberty blockers", "hormone blockers", "medical transition", "youth transition",
    "transgender athletes", "trans sports participation", "trans youth sports",
    "restroom access", "bathroom bill", "trans restroom rights", "gender-neutral restroom",
    "trans youth rights", "trans youth protection", "trans youth therapy", "conversion therapy",
    "gender counseling", "trans youth counseling", "gender marker", "gender on ID", "gender recognition",
    "legal gender change", "trans rights", "trans discrimination", "gender identity protection",
    "gender expression protection", "trans employment rights", "trans hate crimes", "trans protections",
    "trans military ban", "trans military service", "trans inclusive policies", 
    "trans education rights", "trans student rights", "gender-affirming procedures", "trans surgeries",
     "voice therapy", "trans voice therapy", "trans exclusion policies",
    "trans youth support", "trans youth groups", "trans youth organizations", "trans youth legal rights",
    "trans youth medical rights", "trans youth parental rights", "trans youth legal protection",
    "trans youth medical protection", "trans youth education rights", "trans youth school rights",
    "trans youth mental health", "trans youth support services", "trans youth resources"
    ]
    for keyword in KEYWORDS:
        logging.error(f"Fetching bills for keyword: {keyword}")
        bills_data = fetch_all_bills_by_keyword(keyword)
        api_state.total_items_fetched += len(bills_data)
        
        logging.error(f"Storing {len(bills_data)} bills in the database.")
        store_bill(bills_data, api_state=api_state)
        
        # logging summary stats after each keyword
        logging.error(f"Total Requests Made: {api_state.total_requests}")
        logging.error(f"Total Items Fetched: {api_state.total_items_fetched}")
        logging.error(f"Total Items Saved: {api_state.total_items_saved}")
        
        time.sleep(delay_time)

def get_bill_summary(congress, bill_type, api_state=None):
    # Check if we're nearing the rate limit, if so, reset.
    if api_state:
        check_and_reset_rate_limit(api_state)

    # Create the API endpoint for this specific bill summary
    endpoint = f"v3/summaries/{congress}/{bill_type}"

    # Make a request to fetch the summary data
    summary_data = make_request(endpoint, api_state=api_state)

    return summary_data

def check_and_reset_rate_limit(api_state):
    if api_state.total_requests >= 990:
        logging.error("Approaching rate limit. Pausing for 1 hour.")
        time.sleep(3600)  # 1 hour
        api_state.total_requests = 0  # Reset the counter

def get_committee_details(congress, chamber, api_state=None, batch_size=100):
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



# Add a function to switch modes
def run_script():
    first_run = True  # Set this to False once the initial population is done

    if first_run:
        logging.error("Populating database...")
        main('populate')
    else:
        logging.error("Maintaining database...")
        main('maintain')

if __name__ == "__main__":
    main()