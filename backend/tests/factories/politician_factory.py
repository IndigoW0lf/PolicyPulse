from factory import Sequence, Faker
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import Politician
from backend import db

class PoliticianFactory(BaseFactory):
    class Meta:
        model = Politician

    id = Sequence(lambda n: n)
    name = Sequence(lambda n: f'Politician Name {n}')
    state = Faker('state_abbr')
    party = Faker('random_element', elements=['Democrat', 'Republican', 'Independent'])
    role = Sequence(lambda n: f'Role {n}')
    profile_link = Sequence(lambda n: f'http://profilelink.com/{n}')
    bioguide_id = Sequence(lambda n: f'BIOG{n}')
    gpo_id = Sequence(lambda n: f'GPO{n}')
    lis_id = Sequence(lambda n: f'LIS{n}')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance