from factory import Sequence, SubFactory
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import Note, Bill
from backend import db

class NoteFactory(BaseFactory):
    class Meta:
        model = Note

    id = Sequence(lambda n: n)
    text = Sequence(lambda n: f'Note Text {n}')
    bill = SubFactory('backend.tests.factories.bill_factory.BillFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance