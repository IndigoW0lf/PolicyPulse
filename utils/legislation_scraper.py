import requests
from bs4 import BeautifulSoup
import time

# URL of the page you want to scrape
URL = 'https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A118%7D'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/"
}

with requests.Session() as session:
    session.headers.update(headers)
    time.sleep(2)  # Introduce a delay
    response = session.get(URL)
    response.raise_for_status()  # Raise an exception for HTTP errors
    html = response.text

# Parse the HTML with Beautiful Soup
soup = BeautifulSoup(html, 'html.parser')

# Extract bill details
bill_type = soup.find('span', class_='visualIndicator').text
bill_number_and_session = soup.find('span', class_='result-heading').a.text
bill_name = soup.find('span', class_='result-title').text
sponsor = soup.find('strong', text='Sponsor:').find_next('a').text
date_introduced = sponsor.split(' (Introduced ')[1].split(')')[0]
cosponsors = soup.find('strong', text='Cosponsors:').find_next('a').text
committees = soup.find('strong', text='Committees:').next_sibling.strip()
latest_action = soup.find('strong', text='Latest Action:').next_sibling.strip()
bill_status = soup.find('ol', class_='stat_leg').find('li', class_='selected').text.strip()

print(f"Bill Type: {bill_type}")
print(f"Bill Number and Session: {bill_number_and_session}")
print(f"Bill Name: {bill_name}")
print(f"Sponsor: {sponsor}")
print(f"Date Introduced: {date_introduced}")
print(f"Number of Cosponsors: {cosponsors}")
print(f"Committees: {committees}")
print(f"Latest Action: {latest_action}")
print(f"Bill Status: {bill_status}")