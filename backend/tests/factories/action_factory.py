from factory import Sequence, SubFactory
import factory
from factories.base_factory import BaseFactory
from backend.database.models import Action, ActionType, Bill
from backend import db

class ActionFactory(BaseFactory):
    class Meta:
        model = Action

    id = Sequence(lambda n: n)
    action_date = factory.Faker('date')
    description = Sequence(lambda n: f'Action Description {n}')
    chamber = factory.Iterator(['House', 'Senate'])
    bill = SubFactory('factories.bill_factory.BillFactory')
    action_type = SubFactory('factories.action_type_factory.ActionTypeFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
