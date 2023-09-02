import pytest
from policyapp.models.loc_summary import LOCSummary

def test_locsummary_creation(init_database):
    # Create a LOCSummary object
    loc_summary = LOCSummary(
        version_code="Introduced",
        chamber="House",
        action_description="Introduced in House",
        summary_text="This is a test summary",
        bill_id=1  # Assuming the first Bill object has an ID of 1
    )

    init_database.session.add(loc_summary)
    init_database.session.commit()

    # Fetch the inserted object from the database
    fetched_loc_summary = LOCSummary.query.get(1)

    # Check if the object was inserted and the fields match
    assert fetched_loc_summary is not None
    assert fetched_loc_summary.version_code == "Introduced"
    assert fetched_loc_summary.chamber == "House"
    assert fetched_loc_summary.action_description == "Introduced in House"
    assert fetched_loc_summary.summary_text == "This is a test summary"
    assert fetched_loc_summary.bill_id == 1