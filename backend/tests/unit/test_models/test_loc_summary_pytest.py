import pytest
from backend.database.models import LOCSummary

def test_locsummary_fields(init_database):
    session = init_database.session

    # Fetch the existing object from the database using session.get
    fetched_loc_summary = session.get(LOCSummary, 1)  # Assuming the ID is 1

    # Check if the object exists and the fields match what's expected
    assert fetched_loc_summary is not None
    assert fetched_loc_summary.version_code == "Introduced"
    assert fetched_loc_summary.chamber == "House"
    assert fetched_loc_summary.action_description == "Introduced in House"
    assert fetched_loc_summary.summary_text == "This is a test summary"
    assert fetched_loc_summary.bill_id == 1  # or whatever ID you expect