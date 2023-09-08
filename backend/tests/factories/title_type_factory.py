import factory
from backend.database.models import TitleType

class TitleTypeFactory(factory.Factory):
    class Meta:
        model = TitleType

    code = factory.Sequence(lambda n: f"HR{n}")
    description = factory.Sequence(lambda n: f"House Resolution {n}")