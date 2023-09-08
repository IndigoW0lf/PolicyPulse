from factory import Sequence
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import Subject
from backend import db

class SubjectFactory(BaseFactory):
    class Meta:
        model = Subject

    id = Sequence(lambda n: n)
    name = Sequence(lambda n: f'Subject Name {n}')
    description = Sequence(lambda n: f'Subject Description {n}')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance