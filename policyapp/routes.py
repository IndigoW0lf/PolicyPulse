from flask import render_template, request, redirect, url_for
from policyapp import app, db
from policyapp.models import Legislation
    
@app.route('/legislations')
def get_legislations():
  legislations = Legislation.query.all()
  return render_template('legislations.html', legislations=legislations)

@app.route('/legislation/<int:id>', methods=['GET'])
def legislation_detail(id):
    legislation = Legislation.query.get(id)
    if not legislation:
        return "Legislation not found", 404
    return render_template('legislation_detail.html', legislation=legislation)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        legislations = Legislation.query.filter(Legislation.title.contains(query)).all()
        return render_template('search_results.html', legislations=legislations)
    return render_template('search.html')

@app.route('/filter', methods=['GET'])
def filter():
    status = request.args.get('status')
    if status:
        legislations = Legislation.query.filter_by(status=status).all()
    else:
        legislations = Legislation.query.all()
    return render_template('filter_results.html', legislations=legislations)