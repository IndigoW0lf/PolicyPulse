import factory
from backend.database.models import Subject

class SubjectFactory(factory.Factory):
    class Meta:
        model = Subject

    name = "Test Subject"
    description = "This is a test subject."