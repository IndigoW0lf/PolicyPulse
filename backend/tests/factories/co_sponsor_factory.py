import factory
from backend.database.models import CoSponsor

class CoSponsorFactory(factory.Factory):
    class Meta:
        model = CoSponsor

    bill_id = 1
    politician_id = 1