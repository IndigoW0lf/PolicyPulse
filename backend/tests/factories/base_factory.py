from factory import Factory, SQLAlchemyModelFactory
from backend import db

class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = db.session