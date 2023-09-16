import os
from lxml import etree
from backend.utils.database import SessionFactory  # Importing centralized session factory
from backend.utils.db_operations import parse_and_save_bill

def load_xml_file(file_path):
    """Loads an XML file and returns the root element."""
    try:
        tree = etree.parse(file_path)
        return tree.getroot()
    except Exception as e:
        print(f"Error loading XML file: {e}")
        return None

def main():
    # Configure the database session to interact with the testing database.
    session = SessionFactory()  # Creating a new session using centralized session factory

    # Specify the path to your XML file here
    xml_file_path = "backend/data/text.xml"

    xml_root = load_xml_file(xml_file_path)
    if xml_root is not None:
        bill = parse_and_save_bill(xml_root, session)  # `bill` was not defined before, fixed it here
        if bill is not None:
            print("Bill parsing successful!")
        else:
            print("Bill parsing failed.")

if __name__ == "__main__":
    main()
