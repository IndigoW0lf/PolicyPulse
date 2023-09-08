import factory
from backend.database.models import RelatedBill

class RelatedBillFactory(factory.Factory):
    class Meta:
        model = RelatedBill

    bill_id = 1
    related_bill_id = 2