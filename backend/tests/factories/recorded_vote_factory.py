from factory import Factory, Sequence
from backend.database.models import RecordedVote
from datetime import datetime
from backend import db

class RecordedVoteFactory(Factory):
    class Meta:
        model = RecordedVote

    id = Sequence(lambda n: n)
    chamber = Sequence(lambda n: f"Chamber {n}")
    congress = Sequence(lambda n: f"Congress {n}")
    date = datetime.utcnow().date()
    full_action_name = Sequence(lambda n: f"Full Action Name {n}")
    roll_number = Sequence(lambda n: f"Roll Number {n}")
    session_number = Sequence(lambda n: f"Session Number {n}")
    url = Sequence(lambda n: f"http://example.com/recorded_vote/{n}")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        cls._meta.sqlalchemy_session.add(instance)
        cls._meta.sqlalchemy_session.commit()
        return instance