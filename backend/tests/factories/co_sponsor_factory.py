import factory
from backend.database.models import CoSponsor

class CoSponsorFactory(factory.Factory):
    class Meta:
        model = CoSponsor

    bill_id = factory.SubFactory('backend.tests.factories.BillFactory')
    politician_id = factory.SubFactory('backend.tests.factories.PoliticianFactory')