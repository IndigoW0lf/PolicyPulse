from factory import Sequence
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import TitleType
from backend import db

class TitleTypeFactory(BaseFactory):
    class Meta:
        model = TitleType

    id = Sequence(lambda n: n)
    code = Sequence(lambda n: f'TITLE_CODE_{n}')
    description = Sequence(lambda n: f'Title Description {n}')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance