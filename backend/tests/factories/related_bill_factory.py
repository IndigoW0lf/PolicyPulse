from factory import Sequence, SubFactory
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import RelatedBill, Bill
from backend import db

class RelatedBillFactory(BaseFactory):
    class Meta:
        model = RelatedBill

    id = Sequence(lambda n: n)
    main_bill = SubFactory('backend.tests.factories.bill_factory.BillFactory')
    related_bill = SubFactory('backend.tests.factories.bill_factory.BillFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance