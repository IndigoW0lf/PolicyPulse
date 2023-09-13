from factory import Sequence, SubFactory, Faker
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import AmendmentAction, Amendment
from backend import db

class AmendmentActionFactory(BaseFactory):
    class Meta:
        model = AmendmentAction

    id = Sequence(lambda n: n)
    action_code = Sequence(lambda n: f'ACTION_CODE_{n}')
    action_date = Faker('date')
    action_time = Faker('time_object')
    committee_name = Sequence(lambda n: f'Committee Name {n}')
    committee_system_code = Sequence(lambda n: f'COM_SYS_CODE_{n}')
    source_system_code = Sequence(lambda n: f'SRC_SYS_CODE_{n}')
    source_system_name = Sequence(lambda n: f'Source System Name {n}')
    action_text = Sequence(lambda n: f'Action Text {n}')
    amendment = SubFactory('backend.tests.factories.amendment_factory.AmendmentFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance