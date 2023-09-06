import pytest
from backend.database.models import LOCSummary
from .conftest import create_locsummary, create_bill

def test_locsummary_fields(session):
    bill = create_bill(session)
    loc_summary = create_locsummary(session, version_code="Introduced", chamber="House", action_description="Introduced in House", summary_text="This is a test summary", bill_id=bill.id)
    
    assert loc_summary is not None
    assert loc_summary.version_code == "Introduced"
    assert loc_summary.chamber == "House"
    assert loc_summary.action_description == "Introduced in House"
    assert loc_summary.summary_text == "This is a test summary"
    assert loc_summary.bill_id == bill.id
