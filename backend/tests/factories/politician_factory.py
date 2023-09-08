import factory
from backend.database.models import Politician

class PoliticianFactory(factory.Factory):
    class Meta:
        model = Politician

    name = "Test Politician"
    state = "Test State"
    party = "Test Party"
    role = "Test Role"
    profile_link = "http://example.com/profile"