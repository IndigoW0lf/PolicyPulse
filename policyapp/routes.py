from flask import Blueprint, jsonify, request
from policyapp import db
from policyapp.models import Action, ActionType, Amendment, Committee, CoSponsor, Bill, LOCSummary, Politician, RelatedBill, Subject, TitleType

bp = Blueprint('routes', __name__)
    
#Bill Routes
@bp.route('/bill')
def get_Bills():
  Bills = Bill.query.all()
  return jsonify([Bill.to_dict() for Bill in Bills])

@bp.route('/bill/<int:id>', methods=['GET'])
def Bill_detail(id):
    Bill = Bill.query.get(id)
    if not Bill:
        return jsonify({"error": "Bill not found"}), 404
    return jsonify(Bill.to_dict())

@bp.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    Bills = Bill.query.filter(Bill.title.contains(query)).all()
    return jsonify([Bill.to_dict() for Bill in Bills])

@bp.route('/filter-bills', methods=['GET'])
def filter_Bills():
    status = request.args.get('status')
    if status:
        Bills = Bill.query.filter_by(status=status).all()
    else:
        Bills = Bill.query.all()
    return jsonify([Bill.to_dict() for Bill in Bills])

# Politician Routes
@bp.route('/politicians')
def get_politicians():
    politicians = Politician.query.all()
    return jsonify([politician.to_dict() for politician in politicians])

@bp.route('/politician/<int:id>', methods=['GET'])
def politician_detail(id):
    politician = Politician.query.get(id)
    if not politician:
         return jsonify({"error": "Politician not found"}), 404
    return jsonify(politician.to_dict())

# CoSponsor Routes
@bp.route('/bill/<int:id>/co-sponsors')
def get_cosponsors(id):
    Bill = Bill.query.get(id)
    if not Bill:
        return jsonify({"error": "Bill not found"}), 404
    co_sponsors = Bill.co_sponsors
    return jsonify([cosponsor.to_dict() for cosponsor in co_sponsors])

@bp.route('/co-sponsor/<int:id>')
def cosponsor_detail(id):
    cosponsor = CoSponsor.query.get(id)
    if not cosponsor:
        return jsonify({"error": "Co-sponsor not found"}), 404
    return jsonify(cosponsor.to_dict())

# RelatedBill Routes
@bp.route('/bill/<int:id>/related-bills')
def get_related_bills(id):
    Bill = Bill.query.get(id)
    if not Bill:
        return jsonify({"error": "Bill not found"}), 404
    related_bills = Bill.related_bills
    return jsonify([related_bill.to_dict() for related_bill in related_bills])

@bp.route('/related-bill/<int:id>')
def related_bill_detail(id):
    related_bill = RelatedBill.query.get(id)
    if not related_bill:
        return jsonify({"error": "Related bill not found"}), 404
    return jsonify(related_bill.to_dict())