import factory
from backend.database.models import Committee

class CommitteeFactory(factory.Factory):
    class Meta:
        model = Committee

    name = "Test Committee"
    chamber = "House"
    committee_code = "TC001"