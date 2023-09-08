import factory
from backend.database.models import Subject

class SubjectFactory(factory.Factory):
    class Meta:
        model = Subject

    name = factory.Sequence(lambda n: f"Test Subject {n}")
    description = factory.Sequence(lambda n: f"This is a test subject {n}.")