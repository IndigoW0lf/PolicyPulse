import factory
from datetime import date
from backend.database.models import Bill

class BillFactory(factory.Factory):
    class Meta:
        model = Bill

    title = "Test Bill"
    summary = "This is a test bill"
    date_introduced = date.today()
    status = "Proposed"
    bill_number = "HR001"
    sponsor_name = "Test Politician"
    committee = "Committee1"
    voting_record = "Yea: 10, Nay: 5"
    full_bill_link = "http://example.com/full_bill_1"
    tags = "Test Bill"
    last_action_date = date.today()
    last_action_description = "Introduced in House"
    congress = "117th"
    bill_type = "HR"
    update_date = date.today()
    xml_content = None
    action_type_id = 1
    sponsor_id = 123
    title_type_id = 9