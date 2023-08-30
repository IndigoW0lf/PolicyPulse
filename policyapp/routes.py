from flask import render_template, request, redirect, url_for
from policyapp import app, db
from policyapp.models import *
    
#Legislation Routes
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

# Politician Routes
@app.route('/politicians')
def get_politicians():
    politicians = Politician.query.all()
    return render_template('politicians.html', politicians=politicians)

@app.route('/politician/<int:id>', methods=['GET'])
def politician_detail(id):
    politician = Politician.query.get(id)
    if not politician:
        return "Politician not found", 404
    return render_template('politician_detail.html', politician=politician)

# CoSponsor Routes
@app.route('/legislation/<int:id>/co-sponsors')
def get_cosponsors(id):
    legislation = Legislation.query.get(id)
    if not legislation:
        return "Legislation not found", 404
    co_sponsors = legislation.co_sponsors
    return render_template('cosponsors.html', co_sponsors=co_sponsors)

@app.route('/co-sponsor/<int:id>')
def cosponsor_detail(id):
    cosponsor = CoSponsor.query.get(id)
    if not cosponsor:
        return "Co-sponsor not found", 404
    return render_template('cosponsor_detail.html', cosponsor=cosponsor)

# RelatedBill Routes
@app.route('/legislation/<int:id>/related-bills')
def get_related_bills(id):
    legislation = Legislation.query.get(id)
    if not legislation:
        return "Legislation not found", 404
    related_bills = legislation.related_bills
    return render_template('related_bills.html', related_bills=related_bills)

@app.route('/related-bill/<int:id>')
def related_bill_detail(id):
    related_bill = RelatedBill.query.get(id)
    if not related_bill:
        return "Related bill not found", 404
    return render_template('related_bill_detail.html', related_bill=related_bill)