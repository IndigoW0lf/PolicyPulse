import json
from datetime import datetime
from lxml import etree
from xml.etree.ElementTree import Element
import logging
from backend.data.loc_summary_versioncode_mapping import version_code_mapping

# Constants
DATE_FORMATS = [
    '%Y-%m-%d',
    '%Y-%m-%dT%H:%M:%SZ'
]


def xml_to_json(xml_str):
    """Converts XML string to JSON."""
    xml_root = etree.fromstring(xml_str)
    json_result = json.dumps({xml_root.tag: xml_to_dict(xml_root)})
    return json_result


def xml_to_dict(xml_root, depth=0):

    if depth > 100:  # Limiting the recursion depth to avoid potential stack overflow
        logging.error("Recursion depth has exceeded the limit in xml_to_dict")
        return {}

    result = {}
    for child in xml_root:
        if len(child):
            # Incrementing the depth with each recursive call
            result[child.tag] = xml_to_dict(child, depth+1)
        else:
            result[child.tag] = child.text

    return result


def get_text(element, xpath):
    """Utility function to get text from an XML element using XPath."""
    result = element.xpath(xpath)
    if result:
        result = result[0]
        if result.text:
            return result.text.strip()  # .strip() to remove any leading/trailing whitespace
    return ""


def parse_date(date_str):
    """Utility function to parse a date string."""
    if date_str and isinstance(date_str, str):
        for date_format in DATE_FORMATS:
            try:
                return datetime.strptime(date_str.strip(), date_format).date()
            except ValueError:
                continue

        logging.error(
            f"Error in parse_date - Failed to parse date_str: '{date_str}'")
        return None
    else:
        return None


version_code_mapping = version_code_mapping
