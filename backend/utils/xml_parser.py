import logging
import os
from lxml import etree
from shutil import copyfile
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
    
    prelim_related_files = 'backend/data/prelim_related_xml_files'
    os.makedirs(prelim_related_files, exist_ok=True)
    
    for xml_file in xml_files:
        try:
            tree = etree.parse(xml_file)
            
            # Extracting the title, summary, and amended bill title text
            title_element = tree.find(".//titles/item[titleType='Official Title as Introduced']/title")
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

                    # Define the destination path
                    dest_path = os.path.join(prelim_related_files, os.path.basename(xml_file))
                    
                    # Check if the file already exists in the destination directory
                    if not os.path.exists(dest_path):
                        # If not, copy the file to the filtered xml files directory
                        copyfile(xml_file, dest_path)
                    else:
                        logging.info(f"File '{os.path.basename(xml_file)}' already exists in the destination directory. Skipping.")
                    
                    break

        except Exception as e:
            logging.error(f"Error processing file {xml_file}: {e}", exc_info=True)

    print(f"Total keywords found: '{keyword_found_count}'")
        
# Specify the directory containing XML files and the keywords to search for
if __name__ == "__main__":
    parse_xml_files('backend/data/test_xml_files', keywords)  
