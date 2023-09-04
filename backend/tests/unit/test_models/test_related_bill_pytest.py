import pytest
from datetime import date
from backend.database.models import RelatedBill, Bill

def test_related_bill_creation(init_database):
    session = init_database.session
    related_bill = RelatedBill(bill_id=1, related_bill_id=2)
    session.add(related_bill)
    session.commit()
    related_bill_from_db = session.query(RelatedBill).first()
    assert related_bill_from_db is not None

def test_related_bill_fields(init_database):
    session = init_database.session
    related_bill = session.query(RelatedBill).first()
    main_bill = session.get(Bill, related_bill.bill_id)
    related = session.get(Bill, related_bill.related_bill_id)
    
    assert main_bill.title == "Test Bill"
    assert related.title == "Related Test Bill"

def test_related_bill_relationship(init_database):
    session = init_database.session
    related_bill = session.query(RelatedBill).first()
    main_bill = session.get(Bill, related_bill.bill_id)
    related = session.get(Bill, related_bill.related_bill_id)
    
    assert related_bill.main_bill.title == main_bill.title
    assert related_bill.related.title == related.title