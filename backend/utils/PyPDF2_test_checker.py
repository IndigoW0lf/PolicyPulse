import os
from lxml import etree
import logging
import requests
from PyPDF2 import PdfReader
from io import BytesIO

# Setup logging
LOG_FILENAME = 'backend/utils/Missouri/MO_pdf_text_extraction_log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the folder containing XMLs
folder_path = "backend/utils/Missouri/MO_Keyword_XMLs"

# Custom headers with User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}

def extract_pdf_link_from_xml(xml_file_path):
    """Extract the PDF link from an XML file."""
    try:
        with open(xml_file_path, 'r', encoding='utf-8') as xml_file:
            tree = etree.parse(xml_file)
            pdf_links = tree.xpath('//BillTextLink/text()')
            return pdf_links[-1] if pdf_links else None
    except Exception as e:
        logging.error(f"Error extracting PDF link from {xml_file_path}. Error: {e}")
        return None

def fetch_pdf_content(pdf_url):
    """Fetch the PDF content from the given URL."""
    try:
        response = requests.get(pdf_url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"Failed to fetch PDF content from {pdf_url}. Error: {e}")
        return None

def read_pdf_content(pdf_content):
    """Read the text from the PDF content."""
    try:
        with BytesIO(pdf_content) as pdf_file:
            reader = PdfReader(pdf_file)
            text = " ".join(page.extract_text() for page in reader.pages)
            return text
    except Exception as e:
        logging.error(f"Error reading text from PDF content. Error: {e}")
        return None

def main():
    logging.info("Starting PDF text extraction script...")

    # Iterate over all files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            xml_file_path = os.path.join(folder_path, filename)

            # Extract the PDF link from the XML
            pdf_link = extract_pdf_link_from_xml(xml_file_path)
            if not pdf_link:
                logging.warning(f"No PDF link found in {filename}. Skipping.")
                continue

            # Fetch the PDF content
            pdf_content = fetch_pdf_content(pdf_link)
            if not pdf_content:
                continue

            # Read and log the text from the PDF content
            text = read_pdf_content(pdf_content)
            if text:
                logging.info(f"Extracted text from PDF linked in {filename}: {text}")

if __name__ == '__main__':
    main()
