from factory import Sequence, Faker
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import PolicyArea
from backend import db

class PolicyAreaFactory(BaseFactory):
    class Meta:
        model = PolicyArea

    id = Sequence(lambda n: n)
    name = Sequence(lambda n: f'Policy Area Name {n}')
    description = Sequence(lambda n: f'Policy Area Description {n}')
    bill_id = Sequence(lambda n: n)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance