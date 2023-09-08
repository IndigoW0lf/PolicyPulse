import factory
from backend.database.models import BillFullText

class BillFullTextFactory(factory.Factory):
    class Meta:
        model = BillFullText

    bill_id = factory.SubFactory('backend.tests.factories.BillFactory')
    title = None
    meta_data = None
    actions = None
    sections = None