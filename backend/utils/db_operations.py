from backend.database.models import Bill
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import TestingConfig as config
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the logger
logger = logging.getLogger(__name__)

# Database configuration
from config import TestingConfig as config

# Create a new session
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def save_to_database(bill):
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

# Import the parse_bill function from the xml_bill_parser module
from backend.utils.xml_bill_parser import parse_bill

# Function to parse and save the bill to the database
def parse_and_save_bill(xml_root):
    # Parse the bill
    bill = parse_bill(xml_root)
    
    # If the bill was parsed successfully, save it to the database
    if bill:
        save_to_database(bill)
