from backend.utils.keywords import keywords as KEYWORDS
from io import BytesIO
from lxml import etree
import logging
import os
from PyPDF2 import PdfReader
import requests
import time


# Setup logging
LOG_FILENAME = 'backend/utils/Missouri/MO_xml_parsing_log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom headers with User-Agent
HEADERS = {
    "User-Agent": "KaiIndigoWolf/kwol121@wgu.edu - Data Retrieval Script"
}

LAST_UPDATE_FILE = 'backend/utils/Missouri/last_update.txt'
LAST_PROCESSED_INDEX_FILE = 'backend/utils/Missouri/last_processed_index.txt'
BATCH_SIZE = 5 

def fetch_initial_xml(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch initial XML. Error: {e}")
        return None
    
def parse_initial_xml(xml_data):
    try:
        root = etree.fromstring(xml_data)
        bill_data = []
        for bill_xml in root.xpath('//BillXML'):
            link = bill_xml.find('BillXMLLink').text
            last_time_run = bill_xml.find('LastTimeRun').text.split(' ')[0]  # Extract only the date
            bill_data.append((link, last_time_run))
        return bill_data
    except Exception as e:
        logging.error(f"Failed to parse initial XML. Error: {e}")
        return []

def fetch_bill_xml(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch bill XML from {url}. Error: {e}")
        return None

def extract_pdf_link(bill_xml_content):
    logging.info("Extracting PDF link...")
    try:
        root = etree.fromstring(bill_xml_content)
        pdf_links = root.xpath('//BillTextLink/text()')
        return pdf_links[-1] if pdf_links else None
    except Exception as e:
        logging.error(f"Failed to extract PDF link. Error: {e}")
        return None

def fetch_pdf_content(pdf_url):
    logging.info(f"Fetching PDF content from {pdf_url}...")
    try:
        response = requests.get(pdf_url, headers=HEADERS)
        response.raise_for_status()
        logging.info(f"Successfully fetched PDF content from {pdf_url}.")
        return response.content
    except requests.RequestException as e:
        logging.error(f"Failed to fetch PDF content from {pdf_url}. Error: {e}")
        return None

def keyword_check_in_pdf(pdf_content):
    logging.info("Checking keywords in PDF...")
    try:
        with BytesIO(pdf_content) as pdf_file:
            reader = PdfReader(pdf_file)
            for i in range(len(reader.pages)):
                text = reader.pages[i].extract_text()
                
                # # Log the extracted text for debugging
                logging.debug(f"Extracted text from page {i + 1}: {text[:300]}...")  # Log only the first 300 characters for brevity
                
                if any(keyword in text for keyword in KEYWORDS):
                    logging.info(f"Keyword found in PDF on page {i + 1}.")
                    return True
            logging.info("No keywords found in PDF.")
            return False
    except Exception as e:
        logging.error(f"Failed to check keywords in PDF. Error: {e}")
        return False

def extract_filename_from_url(url):
    return os.path.basename(url)

def main():
    logging.info("Starting XML parsing script...")

    # Load last update timestamp
    last_update = None
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, 'r') as f:
            last_update = f.read().strip()

    # Load last processed index
    last_processed_index = 0
    if os.path.exists(LAST_PROCESSED_INDEX_FILE):
        with open(LAST_PROCESSED_INDEX_FILE, 'r') as f:
            content = f.read().strip()
            last_processed_index = int(content) if content else 0

    initial_xml_url = "https://documents.house.mo.gov/xml/BillListTest.xml"
    xml_data = fetch_initial_xml(initial_xml_url)
    
    if not xml_data:
        logging.error("Failed to fetch the initial XML data.")
        return

    bill_data = parse_initial_xml(xml_data)
    
    end_index = min(last_processed_index + BATCH_SIZE, len(bill_data))
    logging.info(f"Processing bills from index {last_processed_index} to {end_index}")

    latest_update = last_update
    
    for index in range(last_processed_index, end_index):
        bill_url, last_time_run = bill_data[index]
        logging.info(f"Processing bill {bill_url}...")

        # Compare with last_update
        if last_update and last_time_run <= last_update:
            logging.debug(f"Skipping {bill_url} as it hasn't been updated since the last run.")
            continue
        
        bill_xml_content = fetch_bill_xml(bill_url)
        if not bill_xml_content:
            continue

        pdf_link = extract_pdf_link(bill_xml_content)
        if not pdf_link:
            continue
        
        pdf_content = fetch_pdf_content(pdf_link)
        if not pdf_content:
            continue
        
        if keyword_check_in_pdf(pdf_content):
            original_filename = extract_filename_from_url(bill_url)
            base_name = original_filename.split('.')[0] if '.' in original_filename else original_filename
            updated_filename = f"{base_name}_{last_time_run}.xml"
            file_path = f'backend/utils/Missouri/MO_Keyword_XMLs/{updated_filename}'
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write(bill_xml_content)
                logging.info(f"Saved XML content to {updated_filename}")
            else:
                logging.warning(f"File {updated_filename} already exists. Skipping.")
            
            # Update latest_update if this bill's timestamp is newer
            if not latest_update or last_time_run > latest_update:
                latest_update = last_time_run

            # After each bill is processed
            with open(LAST_PROCESSED_INDEX_FILE, 'w') as f:
                f.write(str(index + 1))
        
        # Sleep for 5 seconds between requests to respect server load
        time.sleep(5)

    # Save the latest update timestamp for the next run
    if latest_update:
        with open(LAST_UPDATE_FILE, 'w') as f:
            f.write(latest_update)

    # Save the last processed index for the next run
    with open(LAST_PROCESSED_INDEX_FILE, 'w') as f:
        f.write(str(end_index))

    # Sleep for 30 minutes to ensure we don't run more frequently than allowed
    logging.info("Completed this batch. Sleeping for 30 minutes...")
    time.sleep(1800)

if __name__ == '__main__':
    main()