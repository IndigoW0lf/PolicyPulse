from factory import Sequence, SubFactory, Faker
from factories.base_factory import BaseFactory
from backend.database.models import LOCSummary, Bill
from backend import db

class LOCSummaryFactory(BaseFactory):
    class Meta:
        model = LOCSummary

    id = Sequence(lambda n: n)
    version_code = Sequence(lambda n: f'VER_{n}')
    chamber = Faker('random_element', elements=['House', 'Senate'])
    action_description = Sequence(lambda n: f'Action Description {n}')
    summary_text = Sequence(lambda n: f'Summary Text {n}')
    bill = SubFactory('factories.bill_factory.BillFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance