import factory
from datetime import date
from backend.database.models import Bill

class BillFactory(factory.Factory):
    class Meta:
        model = Bill

    title = factory.Sequence(lambda n: f"Test Bill {n}")
    summary = factory.Sequence(lambda n: f"This is a test bill {n}")
    date_introduced = date.today()
    status = "Proposed"
    bill_number = factory.Sequence(lambda n: f"HR{100+n}")
    sponsor_name = factory.Sequence(lambda n: f"Test Politician {n}")
    committee = factory.Sequence(lambda n: f"Committee {n}")
    voting_record = "Yea: 10, Nay: 5"
    full_bill_link = factory.Sequence(lambda n: f"http://example.com/full_bill_{n}")
    tags = factory.Sequence(lambda n: f"Test Bill {n}")
    last_action_date = date.today()
    last_action_description = "Introduced in House"
    congress = "117th"
    bill_type = "HR"
    update_date = date.today()
    xml_content = None
    action_type_id = factory.SubFactory('backend.tests.factories.ActionTypeFactory')
    sponsor_id = factory.Sequence(lambda n: n+1)
    title_type_id = factory.Sequence(lambda n: n+1)
