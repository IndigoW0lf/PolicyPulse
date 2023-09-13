from factory import Sequence, SubFactory
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import LOCSummaryCode
from backend import db

class LOCSummaryCodeFactory(BaseFactory):
    class Meta:
        model = LOCSummaryCode

    id = Sequence(lambda n: n)
    version_code = Sequence(lambda n: f'VER_{n}')
    chamber = Sequence(lambda n: f'Chamber {n}')
    action_desc = Sequence(lambda n: f'Action Description {n}')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance