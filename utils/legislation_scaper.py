from bs4 import BeautifulSoup

# Sample HTML (for demonstration purposes)
html = '''
... (your HTML content here) ...
'''

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