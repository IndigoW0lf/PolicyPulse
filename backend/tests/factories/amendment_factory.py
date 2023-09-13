import factory
from factory import Sequence, SubFactory
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import Amendment
from backend import db

class AmendmentFactory(BaseFactory):
    class Meta:
        model = Amendment

    id = Sequence(lambda n: n)
    amendment_number = Sequence(lambda n: f'AMEND_{n}')
    congress = Sequence(lambda n: f'{116+n}th')  # New field
    description = Sequence(lambda n: f'Amendment Description {n}')
    latest_action_date = factory.Faker('date')  # New field
    latest_action_text = Sequence(lambda n: f'Latest Action Text {n}')  # New field
    purpose = Sequence(lambda n: f'Purpose {n}')  # New field
    type = Sequence(lambda n: f'Type {n}')  # New field
    status = Sequence(lambda n: f'Status {n}')  # New field
    bill = SubFactory('backend.tests.factories.bill_factory.BillFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance