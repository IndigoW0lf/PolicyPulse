from factory import Sequence, SubFactory
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import Amendment, AmendedBill
from backend import db

class AmendedBillFactory(BaseFactory):
    class Meta:
        model = AmendedBill

    id = Sequence(lambda n: n)
    congress = Sequence(lambda n: f'Congress {n}')
    number = Sequence(lambda n: f'Number {n}')
    origin_chamber = Sequence(lambda n: f'Chamber {n}')
    origin_chamber_code = Sequence(lambda n: f'CHAMBER_CODE_{n}')
    title = Sequence(lambda n: f'Title {n}')
    type = Sequence(lambda n: f'Type {n}')
    amendment = SubFactory('backend.tests.factories.amendment_factory.AmendmentFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance