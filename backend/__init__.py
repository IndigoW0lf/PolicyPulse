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

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    config = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }

    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'testing')

    app.config.from_object(config.get(config_name, "testing"))

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