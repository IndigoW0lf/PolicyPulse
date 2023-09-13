from factory import Sequence, SubFactory, Faker
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import VetoMessage, Bill
from backend import db

class VetoMessageFactory(BaseFactory):
    class Meta:
        model = VetoMessage

    id = Sequence(lambda n: n)
    date = Faker('date')
    message = Sequence(lambda n: f'Veto Message {n}')
    president = Sequence(lambda n: f'President {n}')
    text = Sequence(lambda n: f'Veto Message Text {n}')
    bill = SubFactory('backend.tests.factories.bill_factory.BillFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance