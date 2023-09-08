from factory import Sequence, SubFactory, Faker
from factories.base_factory import BaseFactory
from backend.database.models import BillFullText, Bill
from backend import db

class BillFullTextFactory(BaseFactory):
    class Meta:
        model = BillFullText

    id = Sequence(lambda n: n)
    title = Sequence(lambda n: f'Bill Full Text Title {n}')
    bill_metadata = Sequence(lambda n: f'{{"metadata": "Metadata {n}"}}')
    actions = Sequence(lambda n: f'{{"actions": "Actions {n}"}}')
    sections = Sequence(lambda n: f'{{"sections": "Sections {n}"}}')
    bill = SubFactory('factories.bill_factory.BillFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance