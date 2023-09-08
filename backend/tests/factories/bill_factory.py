from factory import Sequence, SubFactory, Faker
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import Bill, ActionType, Politician, TitleType
from backend import db

class BillFactory(BaseFactory):
    class Meta:
        model = Bill

    id = Sequence(lambda n: n)
    title = Sequence(lambda n: f'Bill Title {n}')
    summary = Sequence(lambda n: f'Bill Summary {n}')
    date_introduced = Faker('date')
    status = Sequence(lambda n: f'Status {n}')
    bill_number = Sequence(lambda n: f'BILL_{n}')
    sponsor_name = Sequence(lambda n: f'Sponsor Name {n}')
    committee = Sequence(lambda n: f'Committee {n}')
    voting_record = Sequence(lambda n: f'Voting Record {n}')
    full_bill_link = Sequence(lambda n: f'http://fullbilllink.com/{n}')
    tags = Sequence(lambda n: f'Tag {n}')
    last_action_date = Faker('date')
    last_action_description = Sequence(lambda n: f'Last Action Description {n}')
    congress = Sequence(lambda n: f'Congress {n}')
    bill_type = Sequence(lambda n: f'Bill Type {n}')
    update_date = Faker('date')
    xml_content = Sequence(lambda n: f'<xml>Content {n}</xml>')
    action_type = SubFactory('backend.tests.factories.action_type_factory.ActionTypeFactory')
    sponsor = SubFactory('backend.tests.factories.politician_factory.PoliticianFactory')
    title_type = SubFactory('backend.tests.factories.title_type_factory.TitleTypeFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if 'sponsor' in kwargs:
            kwargs['sponsor_name'] = kwargs['sponsor'].name

        instance = super()._create(model_class, *args, **kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance


