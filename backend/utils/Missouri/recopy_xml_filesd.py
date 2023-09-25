import os
import requests

# The directory where your XML files are stored
DIRECTORY_PATH = 'backend/utils/Missouri/MO_Keyword_XMLs'  # Change this to the path of your directory

# Base URL for fetching XML content
BASE_URL = "https://documents.house.mo.gov/xml/231-{}.xml"

def fetch_xml_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch XML content from {url}. Error: {e}")
        return None

def main():
    for filename in os.listdir(DIRECTORY_PATH):
        if filename.endswith(".xml") and ("HB" in filename or "HR" in filename):
            # Extract the HBxx or HRxx part
            bill_part = filename.split('-')[1].split('_')[0]
            
            # Construct the URL
            url = BASE_URL.format(bill_part)
            
            # Fetch XML content
            content = fetch_xml_content(url)
            if content:
                file_path = os.path.join(DIRECTORY_PATH, filename)
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"Updated content for {filename}")

if __name__ == '__main__':
    main()
