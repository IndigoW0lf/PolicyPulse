from backend.database.models import (
    Bill, Action, Amendment, BillFullText, Committee, CoSponsor, 
    LOCSummary, Politician, PolicyArea, RelatedBill, Subject, VetoMessage
)
from sqlalchemy.exc import SQLAlchemyError
from backend import db
import logging

def get_or_create_politician(sponsor_name, sponsor_state):
    politician = Politician.query.filter_by(name=sponsor_name, state=sponsor_state).first()
    if not politician:
        politician = Politician(name=sponsor_name, state=sponsor_state)
        db.session.add(politician)
        db.session.commit()
    return politician

def save_to_database(bill_data):
    try:
        # Step 1: Create or find existing records for related models
        sponsor_data = bill_data.get('sponsor', {})
        sponsor_name = sponsor_data.get('name')
        sponsor_state = sponsor_data.get('state')
        if sponsor_name and sponsor_state:
            sponsor = get_or_create_politician(sponsor_name, sponsor_state)
        else:
            sponsor = None

        # Step 2: Create a new Bill instance
        bill = Bill(
            number=bill_data['number'],
            update_date=bill_data['update_date'],
            origin_chamber=bill_data['origin_chamber'],
            bill_type=bill_data['bill_type'],
            introduced_date=bill_data['introduced_date'],
            congress=bill_data['congress'],
            display_title=bill_data['display_title'],
            official_title=bill_data['official_title'],
            sponsor_id=sponsor.id,
            primary_subject_id=bill_data['primary_subject_id'],
        )
        db.session.add(bill)

        # Step 3: Create new instances for other related models and link them to the Bill instance
        for action_data in bill_data['actions']:
            action = Action(
                action_date=action_data['action_date'],
                text=action_data['text'],
                type=action_data['type'],
                action_code=action_data['action_code'],
                source_system_code=action_data['source_system']['code'],
                source_system_name=action_data['source_system']['name'],
                bill_id=bill.id,
            )
            db.session.add(action)

        # Save amendments
        for amendment_data in bill_data['amendments']:
            amendment = Amendment(
                amendment_number=amendment_data['amendment_number'],
                description=amendment_data['description'],
                date_proposed=amendment_data['date_proposed'],
                status=amendment_data['status'],
                bill_id=bill.id,
            )
            db.session.add(amendment)

        # Save committees
        for committee_data in bill_data['committees']:
            committee = Committee(
                name=committee_data['name'],
                chamber=committee_data['chamber'],
                committee_code=committee_data['committee_code'],
                bill_id=bill.id,
            )
            db.session.add(committee)

        # Save co-sponsors
        for co_sponsor_data in bill_data['coSponsors']:
            co_sponsor = CoSponsor(
                politician_id=co_sponsor_data['politician_id'],
                bill_id=bill.id,
            )
            db.session.add(co_sponsor)

        # Save full bill texts
        for full_bill_text_data in bill_data['fullBillTexts']:
            full_bill_text = BillFullText(
                display_title=full_bill_text_data['display_title'],
                bill_metadata=full_bill_text_data['bill_metadata'],
                actions=full_bill_text_data['actions'],
                sections=full_bill_text_data['sections'],
                bill_id=bill.id,
            )
            db.session.add(full_bill_text)
        
        # Save latest action
        latest_action_data = bill_data['latestAction']
        latest_action = Action(
            action_date=latest_action_data['actionDate'],
            text=latest_action_data['text'],
            action_time=latest_action_data['actionTime'],
            bill_id=bill.id,
            is_latest=True,
        )
        db.session.add(latest_action)
        db.session.commit()
        
        # Save policy areas
        for policy_area_data in bill_data['policyAreas']:
            policy_area = PolicyArea(
                name=policy_area_data['name'],
                bill_id=bill.id,
            )
            db.session.add(policy_area)

        # Save related bills
        for related_bill_data in bill_data['relatedBills']:
            related_bill = RelatedBill(
                related_bill_id=related_bill_data['related_bill_id'],
                bill_id=bill.id,
            )
            db.session.add(related_bill)

         # Save subjects
        for subject_data in bill_data['subjects']['legislativeSubjects']:
            subject = Subject(
                name=subject_data['name'],
                bill_id=bill.id,
            )
            db.session.add(subject)

        # Save billSubjects
        for subject_data in bill_data['subjects']['billSubjects']:
            subject = Subject(
                name=subject_data['name'],
                bill_id=bill.id,
            )
            db.session.add(subject)

        # Save otherSubjects
        for subject_data in bill_data['subjects']['otherSubjects']:
            subject = Subject(
                name=subject_data['name'],
                parent_subject=subject_data['parentSubject']['name'],
                bill_id=bill.id,
            )
            db.session.add(subject)

        # Save primarySubjects
        for subject_data in bill_data['subjects']['primarySubjects']:
            subject = Subject(
                name=subject_data['name'],
                parent_subject=subject_data['parentSubject']['name'],
                bill_id=bill.id,
            )
            db.session.add(subject)

        # Save summaries
        summary_data = bill_data['summaries']
        if summary_data:
            loc_summary = LOCSummary(
                versions=summary_data['versions'],
                bill_id=bill.id,
            )
            db.session.add(loc_summary)

            
        # Save text versions
        for text_version_data in bill_data['textVersions']:
            text_version = BillFullText(
                type=text_version_data['type'],
                date=text_version_data['date'],
                url=text_version_data['url'],
                bill_id=bill.id,
            )
        db.session.add(text_version)

        #Save veto messages
        for veto_message_data in bill_data['vetoMessages']:
            veto_message = VetoMessage(
                date=veto_message_data['date'],
                message=veto_message_data['message'],
                president=veto_message_data['president'],
                text=veto_message_data['text'],
                bill_id=bill.id,
            )
            db.session.add(veto_message)
            
        db.session.commit()
    
    except SQLAlchemyError as e:
      logging.error(f"Database error: {e}", exc_info=True)
      db.session.rollback()
    except Exception as e:
      logging.error(f"Unexpected error: {e}", exc_info=True)
      db.session.rollback()
