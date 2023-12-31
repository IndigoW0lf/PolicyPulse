from datetime import datetime
from factory import Sequence, SubFactory, Faker
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import CoSponsor, Bill, Politician
from backend import db

class CoSponsorFactory(BaseFactory):
    class Meta:
        model = CoSponsor

    id = Sequence(lambda n: n)
    sponsorship_date = Faker('date')  # New field
    created_at = Faker('date_time')  # New field
    updated_at = Faker('date_time')  # New field
    bill = SubFactory('backend.tests.factories.bill_factory.BillFactory')
    politician = SubFactory('backend.tests.factories.politician_factory.PoliticianFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance