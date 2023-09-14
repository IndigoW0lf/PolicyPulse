import logging
import os
from lxml import etree
from config import Config
from backend.utils.keywords import keywords

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_xml_files(directory, keywords):
    print(f"Directory: {directory}, Keywords: {keywords}")
    xml_files = []
    for root, _, files in os.walk(directory):
        xml_files.extend([os.path.join(root, f) for f in files if f.endswith('.xml')])

    keyword_found_count = 0
    
    for xml_file in xml_files:
        try:
            tree = etree.parse(xml_file)
            
            # Extracting the title, summary, and amended bill title text
            title_element = tree.find(".//titles/item[titleType='Display Title']/title")
            summary_element = tree.find(".//summaries/summary/text")
            amended_title_element = tree.find(".//amendedBill/title")
            
            # Getting the text content from each element, if the element was found
            title_text = title_element.text if title_element is not None else ""
            summary_text = summary_element.text if summary_element is not None else ""
            amended_title_text = amended_title_element.text if amended_title_element is not None else ""

            combined_text = title_text + summary_text + amended_title_text
            
            for keyword in keywords:
                if keyword.lower() in combined_text.lower():
                    logging.info(f"Keyword '{keyword}' found in file: {xml_file}")
                    keyword_found_count += 1
                    break

        except Exception as e:
            logging.error(f"Error processing file {xml_file}: {e}", exc_info=True)

    print(keyword_found_count)
        
# Specify the directory containing your XML files and the keywords to search for
if __name__ == "__main__":
    parse_xml_files(Config.XML_FILES_DIRECTORY, keywords)  
