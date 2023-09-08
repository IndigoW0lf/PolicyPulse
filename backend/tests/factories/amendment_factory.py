import factory
from datetime import date
from backend.database.models import Amendment, AmendmentStatusEnum

class AmendmentFactory(factory.Factory):
    class Meta:
        model = Amendment

    amendment_number = factory.Sequence(lambda n: f"A{100+n}")
    description = factory.Sequence(lambda n: f"Test Amendment {n}")
    date_proposed = date.today()
    bill_id = factory.SubFactory('backend.tests.factories.BillFactory')
    status = AmendmentStatusEnum.PROPOSED