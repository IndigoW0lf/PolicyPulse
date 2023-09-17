from backend import db, create_app
from backend.database.models import Bill, Law, Note, Action, ActionCode, ActionType, BillFullText, BillTitle, Committee, CoSponsor, LOCSummary, PolicyArea, Politician, RecordedVote, RelatedBill, Subject, VetoMessage 

app = create_app()

with app.app_context():  # This is necessary to use the db object outside of a Flask route
    for Model in [Bill, Law, Note, Action, ActionCode, ActionType, BillFullText, BillTitle, Committee, CoSponsor, LOCSummary, PolicyArea, Politician, RecordedVote, RelatedBill, Subject, VetoMessage]: 
        print(f"Querying table {Model.__tablename__}")
        result = db.session.query(Model).limit(5).all()  # Adjust the limit as needed
        for row in result:
            print(row.__dict__)
