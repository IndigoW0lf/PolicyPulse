import factory
from factory import Sequence, SubFactory
from factories.base_factory import BaseFactory
from backend.database.models import Amendment, Bill, AmendmentStatusEnum
from backend import db

class AmendmentFactory(BaseFactory):
    class Meta:
        model = Amendment

    id = Sequence(lambda n: n)
    amendment_number = Sequence(lambda n: f'AMEND_{n}')
    description = Sequence(lambda n: f'Amendment Description {n}')
    date_proposed = factory.Faker('date')
    status = factory.Iterator(AmendmentStatusEnum)
    bill = SubFactory('factories.bill_factory.BillFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance