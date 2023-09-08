import factory
from backend.database.models import Committee

class CommitteeFactory(factory.Factory):
    class Meta:
        model = Committee

    name = factory.Sequence(lambda n: f"Test Committee {n}")
    chamber = "House"
    committee_code = factory.Sequence(lambda n: f"TC{100+n}")