from backend.utils.xml_bill_parser import parse_bill
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the logger
logger = logging.getLogger(__name__)

def save_to_database(bill, session):
    try:
        # Add the bill object to the session
        session.add(bill)
        
        # Commit the transaction
        session.commit()
        
        # Log the success
        logger.info("Bill saved successfully")

    except Exception as e:
        # Roll back the transaction in case of error
        session.rollback()
        
        # Log the error
        logger.error(f"Error saving bill to database: {e}")


# Function to parse and save the bill to the database
def parse_and_save_bill(xml_root, session):
    # Parse the bill
    bill = parse_bill(xml_root, session)
    
    # If the bill was parsed successfully, save it to the database
    if bill:
        save_to_database(bill, session)
