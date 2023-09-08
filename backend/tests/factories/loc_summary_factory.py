import factory
from backend.database.models import LOCSummary

class LOCSummaryFactory(factory.Factory):
    class Meta:
        model = LOCSummary

    version_code = "Introduced"
    chamber = "House"
    action_description = "Introduced in House"
    summary_text = "This is a test summary"
    bill_id = 1