from factory import Sequence
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import ActionType
from backend import db

class ActionTypeFactory(BaseFactory):
    class Meta:
        model = ActionType

    id = Sequence(lambda n: n)
    description = Sequence(lambda n: f'Action Type Description {n}')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance