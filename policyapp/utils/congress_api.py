import requests
import time
from policyapp.models import Bill, Action, Amendment, Committee, db  # Updated Bill to Bill
from config import API_KEY

total_requests = 0
total_items_fetched = 0
total_items_saved = 0

API_BASE_URL = "https://api.congress.gov/"
LIMIT = 250
headers = {
    "X-API-Key": API_KEY,
    "Accept": "application/json"
}

def make_request(endpoint, params={}):
    global total_requests
    offset = 0  # Initialize offset inside the function to start from 0 for each new endpoint request
    all_data = []  # List to accumulate all data across paginated requests

    while True:
        # Update params with limit and offset for pagination
        params.update({"limit": LIMIT, "offset": offset})

        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            # Assuming the main data is in a key named 'results' (adjust if different)
            if 'results' in data:
                all_data.extend(data['results'])

                # If the length of the data is less than the limit, it means we've fetched all the data
                if len(data['results']) < LIMIT:
                    break

                # Increase the offset for the next batch
                offset += LIMIT

                # Introduce a delay of 5 seconds to avoid hitting the rate limit
                time.sleep(5)

                # Increment the request counter
                total_requests += 1  
                
                if total_requests >= 990:
                    print("Approaching rate limit. Pausing for 1 hour.")
                    time.sleep(3600)  # sleep for 1 hour (3600 seconds)
                    total_requests = 0  # Reset the counter

            else:
                break  # Break out of the loop if 'results' key is not present

        except requests.RequestException as e:
            print(f"Error fetching data from {endpoint}: {e}")
            break  # Break out of the loop in case of an error

    return all_data  # Return the accumulated data

# Bill Endpoint
def fetch_all_bills_by_keyword(keyword):
    endpoint = "bill"
    all_data = []
    page = 1

    while True:
        data = make_request(endpoint, params={"search": keyword, "page": page})
        if not data:
            break

        all_data.extend(data.get('bills', []))

        if "next" not in data.get('Pagination', {}):
            break

        page += 1

    return all_data

def fetch_bill_actions(bill_id):
    global total_requests
    if total_requests >= 990:
        print("Approaching rate limit. Pausing for 1 hour.")
        time.sleep(3600)
        total_requests = 0
    endpoint = f"bill/{bill_id}/actions"
    total_requests += 1
    return make_request(endpoint)

def fetch_bill_amendments(bill_id):
    global total_requests
    if total_requests >= 990:
        print("Approaching rate limit. Pausing for 1 hour.")
        time.sleep(3600)
        total_requests = 0
    endpoint = f"bill/{bill_id}/amendments"
    total_requests += 1
    return make_request(endpoint)

def fetch_bill_committees(bill_id):
    global total_requests
    if total_requests >= 990:
        print("Approaching rate limit. Pausing for 1 hour.")
        time.sleep(3600)
        total_requests = 0
    endpoint = f"bill/{bill_id}/committees"
    total_requests += 1
    return make_request(endpoint)

def store_bill(data, batch_size=50):
    global total_items_saved
    counter = 0
    for item in data:
        bill = Bill(
            title=item.get('title', ''),
            summary=item.get('summary', ''),
            bill_number=item.get('billNumber', ''),
            sponsor_name=item.get('sponsor', ''),  # Note: Changed 'sponsor' to 'sponsor_name' to match your model
            date_introduced=item.get('introducedDate', None),
            status=item.get('status', ''),
            committee=",".join(item.get('committees', [])),  # Assuming committees is a list
            full_text_link=item.get('textUrl', ''),
            tags=",".join(item.get('subjects', [])),  # Using subjects as tags
            last_action_date=item.get('latestActionDate', None),
            last_action_description=item.get('latestAction', ''),
        )
        db.session.add(bill)
        
        # Fetch and store related data
        actions = fetch_bill_actions(item.get('bill_id'))
        if actions:
            for action in actions:
                action_record = Action(
                    action_date=action.get('date', None),
                    description=action.get('description', ''),
                    chamber=action.get('chamber', ''),
                    bill_id=bill.id  # Linking to the bill
                )
                db.session.add(action_record)
        
        amendments = fetch_bill_amendments(item.get('bill_id'))
        if amendments:
            for amendment in amendments:
                amendment_record = Amendment(
                    amendment_number=amendment.get('number', ''),
                    description=amendment.get('description', ''),
                    date_proposed=amendment.get('proposedDate', None),
                    status=amendment.get('status', ''),
                    bill_id=bill.id  # Linking to the bill
                )
                db.session.add(amendment_record)
        
        committees = fetch_bill_committees(item.get('bill_id'))
        if committees:
            for committee in committees:
                committee_record = Committee(
                    name=committee.get('name', ''),
                    chamber=committee.get('chamber', ''),
                    committee_code=committee.get('systemCode', ''),
                )
                db.session.add(committee_record)
        
        counter += 1
        total_items_saved += 1

        if counter >= batch_size:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"An error occurred: {e}")
            counter = 0  # Reset the counter

    # Commit any remaining items
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while saving to database: {e}")
        total_items_saved += 1  # Increment the items saved counter for each item saved

def main(mode='populate'):
    global total_items_fetched
    if mode == 'populate':
        delay_time = 3.6  # 1000 requests/hour
    elif mode == 'maintain':
        delay_time = 300  # Run every 5 minutes when in maintenance mode
    else:
        print("Invalid mode")
        return
    
    keywords = [
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
    for keyword in keywords:
        print(f"Fetching bills for keyword: {keyword}")
        bills_data = fetch_all_bills_by_keyword(keyword)
        total_items_fetched += len(bills_data)  # Increment the items fetched counter
        print(f"Storing {len(bills_data)} bills in the database.")
        store_bill(bills_data)
        
        # Print summary stats after each keyword
        print(f"Total Requests Made: {total_requests}")
        print(f"Total Items Fetched: {total_items_fetched}")
        print(f"Total Items Saved: {total_items_saved}")

        time.sleep(delay_time)  # Adjusted delay based on mode

# Summaries Endpoint
def get_bill_summary(congress, bill_type):
    global total_requests
    if total_requests >= 990:
        print("Approaching rate limit. Pausing for 1 hour.")
        time.sleep(3600)
        total_requests = 0
    endpoint = f"v3/summaries/{congress}/{bill_type}"
    total_requests += 1
    return make_request(endpoint)

# Committee Endpoint
def get_committee_details(congress, chamber):
    global total_requests
    if total_requests >= 990:
        print("Approaching rate limit. Pausing for 1 hour.")
        time.sleep(3600)
        total_requests = 0
    endpoint = f"v3/committee/{congress}/{chamber}"
    total_requests += 1
    return make_request(endpoint)

# Add a function to switch modes
def run_script():
    first_run = True  # Set this to False once the initial population is done

    if first_run:
        print("Populating database...")
        main('populate')
    else:
        print("Maintaining database...")
        main('maintain')

if __name__ == "__main__":
    main()