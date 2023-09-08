import factory
from datetime import date
from backend.database.models import Action

class ActionFactory(factory.Factory):
    class Meta:
        model = Action

    action_date = date.today()
    description = factory.Sequence(lambda n: f"Test Action Description {n}")
    chamber = "House"
    bill_id = factory.SubFactory('backend.tests.factories.BillFactory')
    action_type_id = factory.SubFactory('backend.tests.factories.ActionTypeFactory')