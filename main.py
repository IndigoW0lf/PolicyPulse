import os
from lxml import etree
from backend import db
from backend.utils.database import SessionFactory, engine  # Importing centralized session factory
from backend.utils.db_operations import parse_and_save_bill
from backend.utils.xml_bill_parser import parse_amendments, parse_amended_bill
from sqlalchemy import text


def load_xml_file(file_path):
    """Loads an XML file and returns the root element."""
    try:
        tree = etree.parse(file_path)
        return tree.getroot()
    except Exception as e:
        print(f"Error loading XML file: {e}")
        return None
    

def reset_sequences():
    """Reset sequences in the database to start from 1."""
    with engine.connect() as connection:
        statements = [
            text("ALTER SEQUENCE action_code_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE action_type_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE committee_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE loc_summary_code_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE politician_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE subject_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE bill_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE action_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE amendment_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE bill_full_text_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE bill_title_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE co_sponsor_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE law_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE loc_summary_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE note_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE policy_area_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE recorded_vote_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE related_bill_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE amended_bill_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE amendment_action_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE amendment_link_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE subcommittee_id_seq RESTART WITH 1;"),
            text("ALTER SEQUENCE bill_relationship_id_seq RESTART WITH 1;")
        ]
        
        for statement in statements:
            try:
                connection.execute(statement)
            except Exception as e:
                print(f"Error resetting sequence with statement '{statement}': {e}")
        connection.commit()


def main():

    
    # Configure the database session to interact with the testing database.
    session = SessionFactory()  # Creating a new session using centralized session factory

    reset_sequences()  # Reset sequences in the database to start from 1
    
    # Specify the path to the directory containing your XML files here
    xml_directory_path = "backend/data/prelim_related_xml_files"

    # Get a list of all files in the directory
    files_in_directory = os.listdir(xml_directory_path)
    
    # Filter the list to only include .xml files
    xml_files = [file for file in files_in_directory if file.endswith(".xml")]

    success_count = 0
    failure_count = 0

    for xml_file in xml_files:
        try:
            xml_file_path = os.path.join(xml_directory_path, xml_file)
            
            xml_root = load_xml_file(xml_file_path)
            if xml_root is not None:
                bill = parse_and_save_bill(xml_root, session)
                if bill is not None:
                    # print(f"Bill parsing successful for file: {xml_file}")
                    success_count += 1
                else:
                    print(f"{xml_file}")
                    failure_count += 1
        except Exception as e:
            print(f"An error occurred while processing file {xml_file}: {e}")
            failure_count += 1

    print(f"Total successful parses: {success_count}")
    print(f"Total failed parses: {failure_count}")

if __name__ == "__main__":
    main()
