import factory
from backend.database.models import ActionType
from factory import Factory, Sequence

class ActionTypeFactory(Factory):
    class Meta:
        model = ActionType

    description = Sequence(lambda n: f'Action Type {n}')
