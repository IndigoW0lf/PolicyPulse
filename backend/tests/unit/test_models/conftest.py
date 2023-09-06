import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from backend import create_app, db

@pytest.fixture(scope='function', autouse=True)
def init_database():
    from backend.database.models import Bill, Politician, ActionType, Committee, TitleType, Action, Amendment, CoSponsor, LOCSummary, RelatedBill, Subject
    app = create_app('testing')
    with app.app_context():
        db.session.rollback()  # Ensure session is in a clean state
        db.create_all()

        try:
            nested_session = db.session.begin_nested()
            print("Nested session started")

            # Create ActionType first and commit
            action_type = ActionType.query.filter_by(description="Bill is introduced").first()
            if not action_type:
                action_type = ActionType(description="Bill is introduced")
                db.session.add(action_type)
                db.session.flush()

            # Create Politician and commit
            existing_politician = Politician.query.filter_by(name="Test Politician").first()
            if existing_politician:
                politician = existing_politician
            else:
                politician = Politician(
                    name="Test Politician",
                    state="Test State",
                    party="Test Party",
                    role="Test Role",
                    profile_link="http://example.com/profile"
                )
                db.session.add(politician)
                db.session.flush()

            # Create TitleType and commit
            existing_title_type = TitleType.query.filter_by(code="HR").first()
            if existing_title_type:
                title_type = existing_title_type
            else:
                title_type = TitleType(
                    code="HR",
                    description="House Resolution"
                )
                db.session.add(title_type)
                db.session.flush()

            # Create Committee and commit
            existing_committee = Committee.query.filter_by(committee_code="TC001").first()
            if not existing_committee:
                committee = Committee(
                    name="Test Committee",
                    chamber="House",
                    committee_code="TC001"
                )
                db.session.add(committee)
                db.session.flush()

            # Create Bill using the committed IDs
            bill = None
            existing_bill = Bill.query.filter_by(bill_number="HR001").first()
            if not existing_bill:
                bill = Bill(
                    id=1,
                    title="Test Bill",
                    summary="This is a test bill",
                    date_introduced=date.today(),
                    status="Proposed",
                    bill_number="HR001",
                    sponsor_name="Test Politician",
                    sponsor_id=politician.id,
                    action_type_id=action_type.id,
                    title_type_id=title_type.id,
                    committee="Committee1",
                    voting_record="Yea: 10, Nay: 5",
                    full_bill_link="http://example.com/full_bill_1",
                    tags="Test Bill",
                    last_action_date=date.today(),
                    last_action_description="Introduced in House"
                )
                db.session.add(bill)
                db.session.flush()
            else:
                bill = existing_bill

            # Create Bill 2 with id=2 using similar logic
            bill2 = None
            existing_bill2 = Bill.query.filter_by(bill_number="HR002").first()
            if not existing_bill2:
                bill2 = Bill(
                    id=2,
                    title="Related Test Bill",
                    summary="This is a test summary for Bill 2",
                    date_introduced=date.today(),
                    status="Proposed",
                    bill_number="HR002",
                    sponsor_name="Test Politician",
                    sponsor_id=politician.id,
                    action_type_id=action_type.id,
                    title_type_id=title_type.id,
                    committee="Test Committee",
                    voting_record="Yea: 8, Nay: 7",
                    full_bill_link="http://example.com/full_text_2",
                    tags="Test Bill 2",
                    last_action_date=date.today(),
                    last_action_description="Introduced in House"
                )
                db.session.add(bill2)
                db.session.flush()
            else:
                bill2 = existing_bill2

            # Create RelatedBill using the committed Bill IDs
            existing_related_bill = RelatedBill.query.filter_by(bill_id=bill.id, related_bill_id=bill2.id).first()
            if not existing_related_bill:
                related_bill = RelatedBill(
                    bill_id=bill.id,
                    related_bill_id=bill2.id
                )
                db.session.add(related_bill)
                db.session.flush()
            else:
                related_bill = existing_related_bill

            # Create Action using the committed Bill ID
            existing_action = Action.query.filter_by(description="Test Action Description").first()
            if not existing_action:
                action = Action(
                    action_date=date.today(),
                    bill_id=bill.id,
                    action_type_id=action_type.id,
                    description="Test Action Description",
                    chamber="House"
                )
                db.session.add(action)
                db.session.flush()

            # Create Action using the committed Bill ID
            existing_action = Action.query.filter_by(description="Test Action Description").first()
            if not existing_action:
                action = Action(
                    action_date=date.today(),
                    bill_id=bill.id,
                    action_type_id=action_type.id,
                    description="Test Action Description",
                    chamber="House"
                )
                db.session.add(action)
                db.session.flush()

            # Establish relationship between Bill and Committee
            if bill and committee:
                committee.bills.append(bill)
                db.session.flush()

            # Create Subject and commit
            existing_subject = Subject.query.filter_by(name="Test Subject").first()
            if not existing_subject:
                subject = Subject(
                    name="Test Subject",
                    description="This is a test subject."
                )
                db.session.add(subject)
                db.session.flush()

                # Associate the subject with a bill
                if bill2:
                    subject.bills.append(bill2)
                    db.session.flush()

            # Create Amendment using the committed Bill ID and commit
            existing_amendment = Amendment.query.filter_by(amendment_number="A001").first()
            if not existing_amendment:
                amendment = Amendment(
                    amendment_number="A001",
                    description="Test Amendment",
                    date_proposed=date.today(),
                    status="Proposed",
                    bill_id=bill.id
                )
                db.session.add(amendment)
                db.session.flush()

            # Create CoSponsor using the committed Bill and Politician IDs and commit
            existing_co_sponsor = CoSponsor.query.filter_by(bill_id=bill.id, politician_id=politician.id).first()
            if not existing_co_sponsor:
                co_sponsor = CoSponsor(
                    bill_id=bill.id,
                    politician_id=politician.id
                )
                db.session.add(co_sponsor)
                db.session.flush()

            # Create LOCSummary using the committed Bill ID and commit
            existing_loc_summary = LOCSummary.query.filter_by(version_code="Introduced").first()
            if not existing_loc_summary:
                loc_summary = LOCSummary(
                    version_code="Introduced",
                    chamber="House",
                    action_description="Introduced in House",
                    summary_text="This is a test summary",
                    bill_id=bill.id
                )
                db.session.add(loc_summary)
                db.session.flush()
            
            print("About to commit nested session")
            nested_session.commit()
            print("Nested session committed")

        except (IntegrityError, Exception) as e:
            print(f"Exception occurred: {e}")
            db.session.rollback()
            print("Error occurred, rolling back session")
    
        yield db

        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def session(init_database):
    db = init_database
    db.session.begin_nested()
    yield db.session
    db.session.rollback()