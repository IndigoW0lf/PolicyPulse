from backend.data.tag_list import tags
from backend.database.models import Bill
from backend.utils.database import SessionFactory
from backend.utils.xml_helper import get_text
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
    filename='backend/database/logs/gpt_topic_tagging.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] - %(message)s'
)

# Create logger instance
logger = logging.getLogger(__name__)

# # Add a console handler to the logger
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# console_handler.setFormatter(logging.Formatter(
#     '%(asctime)s [%(levelname)s] - %(message)s'))
# logger.addHandler(console_handler)


# def get_tags_for_bill(bill_summary_content):
#     """Get tags for a bill using GPT-4."""
#     prompt = f"Given the following bill content: '{bill_summary_content}', suggest the relevant subject tags for this bill from the following list: {', '.join(tags)}. Do not suggest any tags outside of this list. Answer with just the relevant tags, separated by commas."

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )

#     suggested_tags_raw = response.choices[0].message['content'].strip().replace(
#         "Tags:", "")
#     suggested_tags = [tag.strip() for tag in suggested_tags_raw.split(
#         ",") if tag.strip() in tags]
#     return suggested_tags

def get_tags_for_bill(bill_summary_content):
    """Mock function to return a fixed set of tags without using GPT."""
    # Return a fixed set of tags for testing purposes
    return ["WhatItDo", "TestingTag"]


def tag_bills_and_update_db(directory):
    xml_files = [os.path.join(root, f) for root, _, files in os.walk(
        directory) for f in files if f.endswith('.xml')]

    with SessionFactory() as session:
        for xml_file in xml_files:
            try:
                tree = etree.parse(xml_file)
                bill_details = tree.xpath('//billStatus/bill')[0]

                bill_number = get_text(bill_details, 'number')
                title_elements = bill_details.xpath('titles/item')
                for title_element in title_elements:
                    title_type = get_text(title_element, 'titleType')
                    if title_type == 'Display Title':
                        display_title = get_text(title_element, 'title')

                summaries = bill_details.xpath(".//summaries/summary")
                if summaries:
                    if any(x.findtext("updateDate") for x in summaries):
                        latest_summary = sorted(summaries, key=lambda x: x.findtext(
                            "updateDate") if x.findtext("updateDate") else "0000-00-00", reverse=True)[0]
                    else:
                        # Just use the first summary if no updateDate is found
                        latest_summary = summaries[0]
                    summary_text = get_text(latest_summary, "text")
                    # # Log the summary
                    # logger.info(f"Summary for {xml_file}: {summary_text}")
                else:
                    # Log a warning if no summary is found
                    logger.warning(f"No summary found for {xml_file}")
                    continue

                combined_text = display_title + summary_text

                tags = get_tags_for_bill(combined_text)

                # Add the "LGBTQ" tag to the list of tags
                tags.append("LGBTQ")

                # Fetch the Bill record using the bill_number and title
                bill = session.query(Bill).filter_by(
                    bill_number=bill_number, title=display_title).first()
                if not bill:
                    logger.error(
                        f"Bill with number {bill_number} and title {display_title} not found in database.")
                    continue

                # Use the primary key `id` to update the bill's tags in the database
                session.query(Bill).filter_by(
                    id=bill.id).update({"tags": ", ".join(tags)})
                session.commit()

                logger.info(
                    f"Bill ID: {bill.id}, Number: {bill_number}, Title: {display_title}: Tags - {', '.join(tags)}")

            except Exception as e:
                logger.error(
                    f"Error processing file {xml_file}", exc_info=True)


# Specify the directory containing XML files
directory_path = "backend/data/LGBTQ+_related_xml_files"
tag_bills_and_update_db(directory_path)
