from factory import Factory, Sequence
from backend.database.models import Law
from datetime import datetime
from backend import db

class LawFactory(Factory):
    class Meta:
        model = Law

    id = Sequence(lambda n: n)
    number = Sequence(lambda n: f"Law Number {n}")
    type = Sequence(lambda n: f"Law Type {n}")
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance