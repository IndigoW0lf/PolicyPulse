from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import TestingConfig as config

# Creating an engine and session factory
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
SessionFactory = sessionmaker(bind=engine)