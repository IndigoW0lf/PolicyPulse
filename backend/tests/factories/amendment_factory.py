import factory
from datetime import date
from backend.database.models import Amendment, AmendmentStatusEnum

class AmendmentFactory(factory.Factory):
    class Meta:
        model = Amendment

    amendment_number = "A001"
    description = "Test Amendment"
    date_proposed = date.today()
    bill_id = 1
    status = AmendmentStatusEnum.PROPOSED

