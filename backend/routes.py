from flask import Blueprint, jsonify, request
from backend import db
from lxml import etree
import logging
from backend.utils.xml_bill_parser import parse_bill
from backend.database.models import Action, ActionType, Amendment, Committee, CoSponsor, Bill, LOCSummary, Politician, RelatedBill, Subject 

# bp = Blueprint('routes', __name__)

# # Configure logging
# logging.basicConfig(filename='app.log', level=logging.INFO, 
#                     format='%(asctime)s - %(levelname)s - %(message)s')


# #Bill Routes

# @bp.route('/parse_bill', methods=['POST'])
# def parse_and_save_bill():
#     try:
#         # Get the XML data from the request
#         xml_data = request.data

#         # Parse the XML data to an element tree
#         root = etree.fromstring(xml_data)

#         # Parse the bill
#         bill = parse_bill(root)

#         # Save to database
#         db.session.add(bill)
#         db.session.commit()

#         logging.info("Bill parsed and saved successfully")
#         return jsonify(status="success", message="Bill parsed and saved successfully"), 200

#     except Exception as e:
#         logging.error("Error in processing bill: %s", str(e))
#         return jsonify(status="error", message=str(e)), 500
    
# @bp.route('/bill')
# def get_Bills():
#     page = request.args.get('page', 1, type=int)
#     per_page = request.args.get('per_page', 20, type=int)
#     Bills = Bill.query.paginate(page, per_page, False).items
#     return jsonify([Bill.to_dict() for Bill in Bills])

# @bp.route('/bill/<int:id>', methods=['GET'])
# def Bill_detail(id):
#     Bill = Bill.query.get(id)
#     if not Bill:
#         return jsonify({"error": "Bill not found"}), 404
#     return jsonify(Bill.to_dict())

# # Politician Routes
# @bp.route('/politicians')
# def get_politicians():
#     politicians = Politician.query.all()
#     return jsonify([politician.to_dict() for politician in politicians])

# @bp.route('/politician/<int:id>', methods=['GET'])
# def politician_detail(id):
#     politician = Politician.query.get(id)
#     if not politician:
#          return jsonify({"error": "Politician not found"}), 404
#     return jsonify(politician.to_dict())

# # CoSponsor Routes
# @bp.route('/bill/<int:id>/co-sponsors')
# def get_cosponsors(id):
#     Bill = Bill.query.get(id)
#     if not Bill:
#         return jsonify({"error": "Bill not found"}), 404
#     co_sponsors = Bill.co_sponsors
#     return jsonify([cosponsor.to_dict() for cosponsor in co_sponsors])

# @bp.route('/co-sponsor/<int:id>')
# def cosponsor_detail(id):
#     cosponsor = CoSponsor.query.get(id)
#     if not cosponsor:
#         return jsonify({"error": "Co-sponsor not found"}), 404
#     return jsonify(cosponsor.to_dict())

# # RelatedBill Routes
# @bp.route('/bill/<int:id>/related-bills')
# def get_related_bills(id):
#     Bill = Bill.query.get(id)
#     if not Bill:
#         return jsonify({"error": "Bill not found"}), 404
#     related_bills = Bill.related_bills
#     return jsonify([related_bill.to_dict() for related_bill in related_bills])

# @bp.route('/related-bill/<int:id>')
# def related_bill_detail(id):
#     related_bill = RelatedBill.query.get(id)
#     if not related_bill:
#         return jsonify({"error": "Related bill not found"}), 404
#     return jsonify(related_bill.to_dict())


'''These will be used for the API once I am done with batch importing and switch to API for current updates and bill fetches.'''
# @bp.route('/bill', methods=['POST'])
# def create_bill():
#     bill_data = request.get_json()
#     new_bill = Bill(**bill_data)
#     db.session.add(new_bill)
#     db.session.commit()
#     return jsonify(new_bill.to_dict()), 201

# @bp.route('/search', methods=['POST'])
# def search():
#     query = request.form['query']
#     Bills = Bill.query.filter(Bill.title.contains(query)).all()
#     return jsonify([Bill.to_dict() for Bill in Bills])

# @bp.route('/filter-bills', methods=['GET'])
# def filter_Bills():
#     status = request.args.get('status')
#     if status:
#         Bills = Bill.query.filter_by(status=status).all()
#     else:
#         Bills = Bill.query.all()
#     return jsonify([Bill.to_dict() for Bill in Bills])


