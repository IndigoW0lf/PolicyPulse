from flask import render_template
from backend import create_app
import os
from dotenv import load_dotenv

load_dotenv()

# Get the configuration name from the environment variable
config_name = os.environ.get('FLASK_CONFIG', 'testing')

# Create the Flask app with the specified configuration
app = create_app(config_name)

@app.route('/')
def homepage():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)