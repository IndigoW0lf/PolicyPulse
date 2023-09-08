import factory
from backend.database.models import TitleType

class TitleTypeFactory(factory.Factory):
    class Meta:
        model = TitleType

    code = "HR"
    description = "House Resolution"