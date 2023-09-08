import factory
from backend.database.models import BillFullText

class BillFullTextFactory(factory.Factory):
    class Meta:
        model = BillFullText

    bill_id = 1
    title = None
    meta_data = None
    actions = None
    sections = None