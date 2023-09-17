from backend.utils.xml_bill_parser import parse_bill
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the logger
logger = logging.getLogger(__name__)

def save_to_database(bill, session):
    try:
        # Log the start of the save operation
        logger.info("Attempting to save bill to database...")

        # Add the bill object to the session
        session.add(bill)
        
        # Commit the transaction
        session.commit()
        
        # Log the success
        logger.info("Bill saved successfully")
        return True

    except Exception as e:
        # Roll back the transaction in case of error
        session.rollback()
        
        # Log the error
        logger.error(f"Error saving bill to database: {e}")
        return False

# Function to parse and save the bill to the database
def parse_and_save_bill(xml_root, session):
    try:
        # Log the start of the parsing operation
        logger.info("Starting to parse the bill...")

        # Parse the bill
        bill = parse_bill(xml_root, session)
        
        # If the bill was parsed successfully, save it to the database
        if bill:
            logger.info("Bill parsed successfully, attempting to save to database...")
            save_success = save_to_database(bill, session)
            if save_success:
                logger.info("Bill parsed and saved successfully")
                return bill
            else:
                logger.error("Bill parsing was successful, but saving to database failed")
        else:
            logger.error("Bill parsing failed")
    except Exception as e:
        logger.error(f"An unexpected error occurred in parse_and_save_bill: {e}")

    # If we reach here, return None to indicate that the function did not complete successfully
    return None
