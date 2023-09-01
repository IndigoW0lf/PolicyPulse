import pytest
from policyapp import create_app, db
from policyapp.models import RelatedBill, Bill

@pytest.fixture(scope='module')
def new_related_bill():
    main_bill = Bill(title="Main Test Bill", bill_number="HR001", sponsor_name="Test Politician")
    related_bill = Bill(title="Related Test Bill", bill_number="HR002", sponsor_name="Test Politician")
    related = RelatedBill()
    related.main_bill = main_bill
    related.related = related_bill
    db.session.add_all([main_bill, related_bill, related])
    db.session.commit()

    return related

def test_related_bill_creation(new_related_bill):
    assert new_related_bill is not None

def test_related_bill_fields(new_related_bill):
    assert new_related_bill.main_bill.title == "Main Test Bill"
    assert new_related_bill.related.title == "Related Test Bill"