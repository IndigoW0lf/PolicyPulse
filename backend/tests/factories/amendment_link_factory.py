from factory import Sequence, SubFactory
from backend.tests.factories.base_factory import BaseFactory
from backend.database.models import AmendmentLink, Amendment
from backend import db

class AmendmentLinkFactory(BaseFactory):
    class Meta:
        model = AmendmentLink

    id = Sequence(lambda n: n)
    name = Sequence(lambda n: f'Link Name {n}')
    url = Sequence(lambda n: f'http://example.com/link{n}')
    amendment = SubFactory('backend.tests.factories.amendment_factory.AmendmentFactory')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance