import os
from backend.utils.keywords import keywords
import logging
from lxml import etree

# Set up logging
logging.basicConfig(filename='backend/database/logs/non_relevant_checker.log', level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def extract_all_contexts_from_bill(bill_text, keywords, context_length=15, mode="word"):
    """Extract all surrounding contexts from a bill given a keyword."""
    contexts = []
    index = 0

    while index < len(bill_text):
        index = bill_text.find(keywords, index)
        if index == -1:
            break

        if mode == "character":
            start = max(0, index - context_length)
            end = min(len(bill_text), index + len(keywords) + context_length)
            contexts.append(bill_text[start:end])

        elif mode == "word":
            words = bill_text.split()
            keyword_index = None
            for i, word in enumerate(words):
                if keywords in word:
                    keyword_index = i
                    break

            if keyword_index is not None:
                start = max(0, keyword_index - context_length)
                end = min(len(words), keyword_index + context_length + 1)
                contexts.append(' '.join(words[start:end]))

        index += len(keywords)

    return contexts

def process_bills(directory, keywords):
    xml_files = [os.path.join(root, f) for root, _, files in os.walk(directory) for f in files if f.endswith('.xml')]
    
    for file_number, xml_file in enumerate(xml_files, 1):
        try:
            tree = etree.parse(xml_file)
            summary_element = tree.find(".//summaries/summary/text")
            summary_text = summary_element.text if summary_element is not None else ""

            for keyword in keywords:
                contexts = extract_all_contexts_from_bill(summary_text, keyword)
                for context in contexts:
                    # Here, I could send the context to GPT-3 for summarization
                    # For demonstration purposes, I'm assuming the context itself is the summary
                    summary = context
                    logger.info(f"File {os.path.basename(xml_file)}: {summary}")
            
            # Add a blank line after processing each XML file
            logger.info("")

        except Exception as e:
            logger.error(f"Error processing file {xml_file}", exc_info=True)

# Specify the directory containing XML files
directory_path = "backend/data/prelim_non_related_xml_files"
process_bills(directory_path, keywords)