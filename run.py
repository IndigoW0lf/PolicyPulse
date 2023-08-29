from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:7777@localhost:5432/policypulse'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import routes and models after initializing app and db
import app.routes
from app.models import Legislation

if __name__ == '__main__':
    app.run(debug=True)