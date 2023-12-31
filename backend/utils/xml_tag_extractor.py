import os
from lxml import etree
import json
from config import Config

def extract_tags(element, tag_dict):
    if not isinstance(element.tag, str):
        print(f"Unexpected tag type for {element.tag}: {type(element.tag)}")
        return
    if element.tag not in tag_dict:
        tag_dict[element.tag] = {}

    for child in element:
        extract_tags(child, tag_dict[element.tag])

def parse_xml_file(file_path, unique_tags):
    try:
        parser = etree.XMLParser(ns_clean=True, recover=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()
        extract_tags(root, unique_tags)
        print(f"Processed file: {file_path}")  
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def parse_xml_files(directory, unique_tags):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                parse_xml_file(os.path.join(root, file), unique_tags)

def main():
    unique_tags = {}
    parse_xml_files('backend/utils/Missouri/MO_Keyword_XMLs', unique_tags)

    with open('backend/utils/Missouri/MO_Full_XML_Tags.xml', "w") as f:
        json.dump(unique_tags, f, indent=4)

if __name__ == "__main__":
    main()