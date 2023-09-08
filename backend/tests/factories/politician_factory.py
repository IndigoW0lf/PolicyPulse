import factory
from backend.database.models import Politician

class PoliticianFactory(factory.Factory):
    class Meta:
        model = Politician

    name = factory.Sequence(lambda n: f"Test Politician {n}")
    state = factory.Sequence(lambda n: f"Test State {n}")
    party = factory.Sequence(lambda n: f"Test Party {n}")
    role = factory.Sequence(lambda n: f"Test Role {n}")
    profile_link = factory.Sequence(lambda n: f"http://example.com/profile{n}")