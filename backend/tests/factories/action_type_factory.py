import factory
from backend.database.models import ActionType

class ActionTypeFactory(factory.Factory):
    class Meta:
        model = ActionType

    description = factory.Sequence(lambda n: f"Action Type {n}")