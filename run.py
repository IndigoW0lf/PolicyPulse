from flask import render_template
from policyapp import app
from config import DevelopmentConfig, TestingConfig

# For development
app.config.from_object(DevelopmentConfig)

# For testing
# app.config.from_object(TestingConfig)

@app.route('/')
def homepage():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
