import factory
from backend.database.models import RelatedBill

class RelatedBillFactory(factory.Factory):
    class Meta:
        model = RelatedBill

    bill_id = factory.SubFactory('backend.tests.factories.BillFactory')
    related_bill_id = factory.SubFactory('backend.tests.factories.BillFactory')