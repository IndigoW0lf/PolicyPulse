from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from config import DevelopmentConfig, TestingConfig, ProductionConfig

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'testing')

    if config_name == 'testing':
        app.config.from_object(TestingConfig)
    elif config_name == 'development':
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        raise ValueError("Invalid configuration name")

    db.init_app(app)
    migrate.init_app(app, db)

    from backend import routes
    app.register_blueprint(routes.bp)

    return app


'''
To set Flask Env Variables:

For Development:
export FLASK_APP=__init__.py:create_app
export FLASK_CONFIG=development

For Testing:
export FLASK_APP=__init__.py:create_app
export FLASK_CONFIG=testing

For Production:
export FLASK_APP=__init__.py:create_app
export FLASK_CONFIG=production
'''