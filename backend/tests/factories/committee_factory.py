import factory
from factory import Sequence
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import Committee
from backend import db

class CommitteeFactory(BaseFactory):
    class Meta:
        model = Committee

    id = Sequence(lambda n: n)
    name = Sequence(lambda n: f'Committee Name {n}')
    chamber = factory.Iterator(['House', 'Senate'])
    committee_code = Sequence(lambda n: f'COM_CODE_{n}')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance