import requests
from policyapp.models import Legislation, db
from config import API_KEY

API_BASE_URL = "https://api.congress.gov/"
headers = {
    "X-API-Key": API_KEY,
    "Accept": "application/json"
}

def search_bills_by_keyword(keyword):
    endpoint = "bill"
    response = requests.get(f"{API_BASE_URL}{endpoint}?search={keyword}", headers=headers)
    return response.json()

def fetch_all_bills_by_keyword(keyword):
    endpoint = "bill"
    all_data = []

    page = 1
    while True:
        response = requests.get(f"{API_BASE_URL}{endpoint}?search={keyword}&page={page}", headers=headers)
        data = response.json()
        
        # Assuming 'bills' is the key containing the results
        all_data.extend(data.get('bills', []))

        # Check if there's a next page
        if "next" not in data.get('Pagination', {}):
            break

        page += 1

    return all_data

def store_legislation(data):
    for item in data:
        legislation = Legislation(
            title=item.get('title', ''),
            summary=item.get('summary', ''),
            bill_number=item.get('billNumber', ''),
            sponsor=item.get('sponsor', ''),
            date_introduced=item.get('introducedDate', None),
            status=item.get('status', ''),
            committee=",".join(item.get('committees', [])),  # Assuming committees is a list
            full_text_link=item.get('textUrl', ''),
            tags=",".join(item.get('subjects', [])),  # Using subjects as tags
            last_action_date=item.get('latestActionDate', None),
            last_action_description=item.get('latestAction', ''),
        )
        db.session.add(legislation)
    db.session.commit()

def main():
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
        print(f"Storing {len(bills_data)} bills in the database.")
        store_legislation(bills_data)

if __name__ == "__main__":
    main()
