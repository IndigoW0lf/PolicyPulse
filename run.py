from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/policypulse'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Legislation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    date_introduced = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(100), nullable=True)
    # ... (you can add more fields as needed)

@app.route('/')
def hello_world():
    return 'Hello, Policy Pulse!'

if __name__ == '__main__':
    app.run(debug=True)
