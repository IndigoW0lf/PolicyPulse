from flask import jsonify, request, redirect, url_for
from policyapp import app, db
from policyapp.models import *
    
#Legislation Routes
@app.route('/legislations')
def get_legislations():
  legislations = Legislation.query.all()
  return jsonify([legislation.to_dict() for legislation in legislations])

@app.route('/legislation/<int:id>', methods=['GET'])
def legislation_detail(id):
    legislation = Legislation.query.get(id)
    if not legislation:
        return jsonify({"error": "Legislation not found"}), 404
    return jsonify(legislation.to_dict())

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    legislations = Legislation.query.filter(Legislation.title.contains(query)).all()
    return jsonify([legislation.to_dict() for legislation in legislations])

@app.route('/filter-legislations', methods=['GET'])
def filter_legislations():
    status = request.args.get('status')
    if status:
        legislations = Legislation.query.filter_by(status=status).all()
    else:
        legislations = Legislation.query.all()
    return jsonify([legislation.to_dict() for legislation in legislations])

# Politician Routes
@app.route('/politicians')
def get_politicians():
    politicians = Politician.query.all()
    return jsonify([politician.to_dict() for politician in politicians])

@app.route('/politician/<int:id>', methods=['GET'])
def politician_detail(id):
    politician = Politician.query.get(id)
    if not politician:
         return jsonify({"error": "Politician not found"}), 404
    return jsonify(politician.to_dict())

# CoSponsor Routes
@app.route('/legislation/<int:id>/co-sponsors')
def get_cosponsors(id):
    legislation = Legislation.query.get(id)
    if not legislation:
        return jsonify({"error": "Legislation not found"}), 404
    co_sponsors = legislation.co_sponsors
    return jsonify([cosponsor.to_dict() for cosponsor in co_sponsors])

@app.route('/co-sponsor/<int:id>')
def cosponsor_detail(id):
    cosponsor = CoSponsor.query.get(id)
    if not cosponsor:
        return jsonify({"error": "Co-sponsor not found"}), 404
    return jsonify(cosponsor.to_dict())

# RelatedBill Routes
@app.route('/legislation/<int:id>/related-bills')
def get_related_bills(id):
    legislation = Legislation.query.get(id)
    if not legislation:
        return jsonify({"error": "Legislation not found"}), 404
    related_bills = legislation.related_bills
    return jsonify([related_bill.to_dict() for related_bill in related_bills])

@app.route('/related-bill/<int:id>')
def related_bill_detail(id):
    related_bill = RelatedBill.query.get(id)
    if not related_bill:
        return jsonify({"error": "Related bill not found"}), 404
    return jsonify(related_bill.to_dict())