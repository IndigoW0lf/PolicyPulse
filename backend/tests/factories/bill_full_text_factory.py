from datetime import datetime
from factory import Sequence, SubFactory, Faker
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import BillFullText, Bill
from backend import db

class BillFullTextFactory(BaseFactory):
    class Meta:
        model = BillFullText

    id = Sequence(lambda n: n)
    title = Sequence(lambda n: f'Bill Full Text Title {n}')
    raw_data = Sequence(lambda n: f'Raw Data {n}')  # New field
    bill_metadata = Sequence(lambda n: f'{{"metadata": "Metadata {n}"}}')
    actions = Sequence(lambda n: f'{{"actions": "Actions {n}"}}')
    sections = Sequence(lambda n: f'{{"sections": "Sections {n}"}}')
    parsing_status = Sequence(lambda n: f'Parsing Status {n}')  # New field
    error_message = Sequence(lambda n: f'Error Message {n}')  # New field
    created_at = Faker('date_time')  # New field
    updated_at = Faker('date_time')  # New field
    bill = SubFactory('backend.tests.factories.bill_factory.BillFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance