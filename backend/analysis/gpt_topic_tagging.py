from backend.data.tag_list import tags
from backend.database.models import Bill, LOCSummary
from backend.utils.xml_helper import get_text
from backend.utils.database import SessionFactory
from config import Config
from dotenv import load_dotenv
import logging
from lxml import etree
import openai
import os

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the logger
logging.basicConfig(
    filename='backend/database/logs/gpt_bill_relevancy.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] - %(message)s'
)

# Create logger instance
logger = logging.getLogger(__name__)

# Add a console handler to the logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] - %(message)s'))
logger.addHandler(console_handler)


def get_tags_with_chat_model(bill_content):
    """Get tags for a bill using the gpt-3.5-turbo-16k model."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user",
                "content": f"Given the following bill content: '{bill_content}', and considering the list of tags: {', '.join(tags)}, suggest the most relevant tags for this bill. Note: You can suggest more than one tag, separated by commas."}
        ]
    )
    suggested_tags = response.choices[0].message['content'].strip().split(", ")
    return suggested_tags


def get_tags_with_completion_model(bill_content):
    """Get tags for a bill using the default completion model."""
    prompt = f"Given the following bill content: '{bill_content}', and considering the list of tags: {', '.join(tags)}, suggest the most relevant tags for this bill. Note: You can suggest more than one tag, separated by commas."
    response = openai.Completion.create(
        prompt=prompt,
        max_tokens=150
    )
    suggested_tags = response.choices[0].text.strip().split(", ")
    return suggested_tags


# Get tags using both models
tags_from_chat_model = get_tags_with_chat_model(bill_summary_content)
tags_from_completion_model = get_tags_with_completion_model(
    bill_summary_content)

print("Tags from Chat Model:", tags_from_chat_model)
print("Tags from Completion Model:", tags_from_completion_model)


def get_tags_for_bill(bill_summary_content):
    """Get tags for a bill using GPT-4."""
    prompt = f"Given the following bill content: '{bill_summary_content}', and considering the list of tags: {', '.join(tags)}, suggest the most relevant tags for this bill. Note: You can suggest more than one tag, separated by commas."

    response = openai.Completion.create(
        prompt=prompt,
        max_tokens=150  # Increased max tokens to account for longer prompts
    )

    suggested_tags = response.choices[0].text.strip().split(", ")
    return suggested_tags


def tag_bills_and_update_db(directory):
    xml_files = [os.path.join(root, f) for root, _, files in os.walk(
        directory) for f in files if f.endswith('.xml')]

    with SessionFactory() as session:
        for file_number, xml_file in enumerate(xml_files, 1):
            try:
                tree = etree.parse(xml_file)
                bill_number_element = tree.find(".//billStatus/bill/number")
                bill_number = get_text(bill_number_element, ".//text()")

                # Fetch the Bill record using the bill_number
                bill = session.query(Bill).filter_by(
                    bill_number=bill_number).first()
                if not bill:
                    logger.error(
                        f"Bill with number {bill_number} not found in database.")
                    continue

                # The id of the fetched Bill record is the bill_id you'll use for the LOCSummary table
                bill_id = bill.id

                # Fetch the LOCSummary text using the bill_id
                loc_summary = session.query(
                    LOCSummary).filter_by(bill_id=bill_id).first()
                if not loc_summary:
                    logger.error(
                        f"LOCSummary for bill_id {bill_id} not found in database.")
                    continue

                bill_summary_content = loc_summary.text

                tags = get_tags_for_bill(bill_summary_content)

                # Update the bill's tags in the database
                bill.tags = ", ".join(tags)
                session.commit()

                logger.info(
                    f"File {file_number} (Bill Number: {bill_number}): Tags - {', '.join(tags)}")

            except Exception as e:
                logger.error(
                    f"Error processing file {xml_file}", exc_info=True)


# Specify the directory containing XML files
directory_path = "backend/data/prelim_related_xml_files"
tag_bills_and_update_db(directory_path)
