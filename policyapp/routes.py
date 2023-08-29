from flask import render_template, request, redirect, url_for
from policyapp import app, db
from policyapp.models import Legislation

@app.route('/add-legislation', methods=['GET','POST'])
def add_legislation():
    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        date_introduced = request.form['date_introduced']
        status = request.form['status']
        bill_number = request.form['bill_number']
        sponsor = request.form['sponsor']
        co_sponsors = request.form['co_sponsors']
        committee = request.form['committee']
        voting_record = request.form['voting_record']
        full_text_link = request.form['full_text_link']
        related_bills = request.form['related_bills'] 
        tags = request.form['tags'] 
        last_action_date = request.form['last_action_date']
        last_action_description = request.form['last_action_description']

        new_legislation = Legislation(title=title, summary=summary, date_introduced=date_introduced, status=status, bill_number=bill_number, co_sponsors=co_sponsors, sponsor=sponsor, committee=committee, voting_record=voting_record, full_text_link=full_text_link, related_bills=related_bills, tags=tags, last_action_date=last_action_date, last_action_description=last_action_description)      
        db.session.add(new_legislation)
        db.session.commit()
        return "Legislation added successfully!"
    return render_template('add_legislation.html')
    
@app.route('/legislations')
def get_legislations():
  legislations = Legislation.query.all()
  return render_template('legislations.html', legislations=legislations)

@app.route('/edit-legislation/<int:id>', methods=['GET', 'POST'])
def edit_legislation(id):
    legislation = Legislation.query.get(id)
    if request.method == 'POST':
        legislation.title = request.form['title']
        legislation.summary = request.form['summary']
        legislation.date_introduced = request.form['date_introduced']
        legislation.status = request.form['status']
        legislation.bill_number = request.form['bill_number']
        legislation.sponsor = request.form['sponsor']
        legislation.co_sponsors = request.form['co_sponsors']
        legislation.committee = request.form['committee']
        legislation.voting_record = request.form['voting_record']
        legislation.full_text_link = request.form['full_text_link']
        legislation.related_bills = request.form['related_bills'] 
        legislation.tags = request.form['tags'] 
        legislation.last_action_date = request.form['last_action_date']
        legislation.last_action_description = request.form['last_action_description']
        db.session.commit()
        return "Legislation updated successfully!"
    return render_template('edit_legislation.html', legislation=legislation)

@app.route('/delete-legislation/<int:id>', methods=['POST'])
def delete_legislation(id):
    legislation = Legislation.query.get(id)
    db.session.delete(legislation)
    db.session.commit()
    return "Legislation deleted successfully!"

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