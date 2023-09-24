import logging
import os
import requests
import time
from backend.utils.keywords import keywords
from dotenv import load_dotenv
from database import SessionFactory
from database.models import bill
from lxml import etree

# session = SessionFactory()


# Initialize the logger
logging.basicConfig(
    filename='backend/database/logs/congress_test_log.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] - %(message)s'
)

# Create logger instance
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Set up global variables with default values from environment variables
API_KEY = os.environ.get('API_KEY')
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://api.congress.gov/')
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))
LIMIT = 20 #Total bills I want to fetch
PAGE_SIZE = int(os.environ.get('PAGE_SIZE', 5))

# Set up headers for API requests
HEADERS = {
    "X-API-Key": API_KEY,
    "Accept": "application/json"
}

# Function to make API requests with error handling
def make_request(endpoint, params={}, total_fetched=0):
    """
    Makes a request to the specified endpoint with given parameters.
    
    Args:
    - endpoint (str): The API endpoint to call.
    - params (dict): The parameters to include in the request.
    - total_fetched (int): Total number of records fetched so far. Default is 0.
    
    Returns:
    - tuple: A tuple containing the list of returned data and the next offset.
    """
    offset = params.get("offset", 0)  # Get the offset from params or default to 0  
    all_data = []

    while True:
        params.update({"limit": PAGE_SIZE, "offset": offset})
        
        for retry in range(MAX_RETRIES):
            try:
                logging.debug(f"Making request to endpoint: {endpoint}, params: {params}")
                response = requests.get(f"{API_BASE_URL}{endpoint}", headers=HEADERS, params=params)
                logging.debug(f"Response status code: {response.status_code}")
                
                if response.status_code >= 400:
                    logging.error(f"Received {response.status_code} error for endpoint {endpoint}.")
                    return all_data, offset
                
                response.raise_for_status()
                data = response.json()
                logging.debug(f"Data from API: {data}")

                if 'bills' in data:
                    all_data.extend(data['bills'])
                    if len(data['bills']) < PAGE_SIZE:
                        return all_data, offset
                            
                    offset += PAGE_SIZE
                    time.sleep(3)
                else:
                    logging.error(f"No 'bills' key present in the data. Full response: {data}") 
                    return all_data, offset
                    
                break  # Successfully fetched data, so exit the retry loop
            except requests.RequestException as e:
                logging.error(f"Error fetching data from {endpoint}: {e}. Retrying {retry+1}/{MAX_RETRIES}.")
                time.sleep(2)  # Introducing a small delay before retrying
        else:
            logging.error(f"Reached maximum retries ({MAX_RETRIES}) for endpoint {endpoint}. Moving on.")
            return all_data, offset  # Return the current offset even in case of an error

        if not data.get('bills') or len(data['bills']) < PAGE_SIZE:
            # Ensure we break out of the while loop if there are no more bills
            break

    return all_data, offset  # Return both the data and the offset

def fetch_bills(offset=0, limit=50, from_date=None, to_date=None):
    """
    Fetches bills data using specified parameters.
    
    Args:
    - offset (int): Pagination offset. Default is 0.
    - limit (int): Number of records to fetch. Default is 50.
    - from_date (str): Starting date for the data fetch.
    - to_date (str): Ending date for the data fetch.
    
    Returns:
    - tuple: A tuple containing the list of bills data and the next offset.
    """
    logging.debug("Fetching bills...")
    params = {
        "format": "json",
        "offset": offset,
        "limit": limit,
        "sort": "updateDate+desc"  # Fetch most recently updated bills first
    }
    
    if from_date:
        params["fromDateTime"] = from_date
    if to_date:
        params["toDateTime"] = to_date

    return_data, offset = make_request("v3/bill", params=params) 
    logging.debug(f"Fetched {len(return_data)} bills.")
    
    return return_data, offset  # Return both data and offset

# Fetch the XML version of the bill
def fetch_bill_xml(congress, bill_type, bill_number):
    xml_url = f"https://www.congress.gov/{congress}/bills/{bill_type}{bill_number}/BILLS-{congress}{bill_type}{bill_number}es.xml"
    try:
        response = requests.get(xml_url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching XML for bill {congress}/{bill_type}/{bill_number}: {e}")
        return None

# Modify keyword_analysis function to return matched keywords
def keyword_analysis(text):
    matched_keywords = [keyword for keyword in keywords if keyword.lower() in text.lower()]
    return matched_keywords

# def bill_exists_in_db(congress, bill_type, bill_number, session):
#     existing_bill = session.query(bill).filter_by(congress=congress, bill_type=bill_type, bill_number=bill_number).first()
#     return existing_bill is not None

# def store_xml(congress, bill_type, bill_number, xml_content):
#     # This is just a simple example. You might want to store in a database or a different format.
#     with open(f"stored_xmls/{congress}_{bill_type}_{bill_number}.xml", 'w', encoding='utf-8') as file:
#         file.write(xml_content)

def main():
    bills_data, _ = fetch_bills(offset=0, limit=10)  # Fetching 10 bills for demonstration (updated to handle the tuple return)
    for bill in bills_data:
        congress = str(bill.get('congress'))  # Convert to string to avoid potential type errors
        bill_type = bill.get('type').lower()  # Ensure it's lowercase
        bill_number = str(bill.get('number'))  # Convert to string
        xml_content = fetch_bill_xml(congress, bill_type, bill_number)
        
        if xml_content:
            matched_keywords = keyword_analysis(xml_content)
            
            if matched_keywords:
                logging.info(f"Relevant bill: {bill.get('title')} ({congress}/{bill_type}/{bill_number}). Matched keywords: {', '.join(matched_keywords)}")
                

                # if not bill_exists_in_db(congress, bill_type, bill_number, session):
                #     store_xml(congress, bill_type, bill_number, xml_content)
                # TODO: Once XML is stored, you can parse and save to the database
                # parsed_bill = your_xml_parser(xml_content)
                # save_to_db(parsed_bill)

if __name__ == "__main__":
    main()
