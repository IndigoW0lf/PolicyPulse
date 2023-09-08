import factory
from backend.database.models import LOCSummary

class LOCSummaryFactory(factory.Factory):
    class Meta:
        model = LOCSummary

    version_code = "Introduced"
    chamber = "House"
    action_description = "Introduced in House"
    summary_text = factory.Sequence(lambda n: f"This is a test summary {n}")
    bill_id = factory.SubFactory('backend.tests.factories.BillFactory')