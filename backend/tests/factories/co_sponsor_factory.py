from factory import Sequence, SubFactory
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import CoSponsor, Bill, Politician
from backend import db

class CoSponsorFactory(BaseFactory):
    class Meta:
        model = CoSponsor

    id = Sequence(lambda n: n)
    bill = SubFactory('backend.tests.factories.bill_factory.BillFactory')
    politician = SubFactory('backend.tests.factories.politician_factory.PoliticianFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance