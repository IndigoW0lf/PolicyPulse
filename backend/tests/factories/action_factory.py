import factory
from datetime import date
from backend.database.models import Action

class ActionFactory(factory.Factory):
    class Meta:
        model = Action

    action_date = date.today()
    description = "Test Action Description"
    chamber = "House"
    bill_id = 1
    action_type_id = 1