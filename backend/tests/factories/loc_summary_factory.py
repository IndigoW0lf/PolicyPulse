from factory import Sequence, SubFactory, Faker
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import LOCSummary, Bill
from backend import db

class LOCSummaryFactory(BaseFactory):
    class Meta:
        model = LOCSummary

    id = Sequence(lambda n: n)
    versions = Sequence(lambda n: [
        {
            "version_code": f"VER_{n}",
            "chamber": Faker('random_element', elements=['House', 'Senate']),
            "action_description": f"Action Description {n}",
            "summary_text": f"Summary Text {n}",
            "as_enacted": f"As Enacted {n}",
            "as_introduced": f"As Introduced {n}",
            "as_passed_house": f"As Passed House {n}",
            "as_passed_senate": f"As Passed Senate {n}",
            "as_reported_to_house": f"As Reported to House {n}",
            "as_reported_to_senate": f"As Reported to Senate {n}",
            "latest_major_action": f"Latest Major Action {n}",
            "latest_summary": f"Latest Summary {n}"
        }
    ])
    bill = SubFactory('backend.tests.factories.bill_factory.BillFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
