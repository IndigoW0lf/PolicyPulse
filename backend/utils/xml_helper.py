import json
from datetime import datetime
from lxml import etree
import logging

# Constants
DATE_FORMAT = '%Y-%m-%d'

def xml_to_json(xml_str):
    """Converts XML string to JSON."""
    xml_root = etree.fromstring(xml_str)
    json_result = json.dumps({xml_root.tag: xml_to_dict(xml_root)})
    return json_result


def xml_to_dict(xml_root):
    """Recursively converts XML elements to dictionary."""
    result = {}
    for child in xml_root:
        result[child.tag] = xml_to_dict(child) if len(child) or child is not None else child.text
    return result

def get_text(element, xpath):
    """Utility function to get text from an XML element using XPath."""
    result = element.xpath(f'{xpath}/text()')
    return str(result[0]) if result else None

def parse_date(date_str):
    """Utility function to parse a date string."""
    if date_str and isinstance(date_str, str):
        try:
            return datetime.strptime(date_str.strip(), DATE_FORMAT).date()
        except ValueError as e:
            logging.error(f"Error in parse_date - Failed to parse date_str: '{date_str}', Error: {e}")
            return None
    else:
        return None



# For LOC Summary, using codes to determine chamber.
version_code_mapping = {
    "00": {"chamber": "HOUSE", "action_desc": "Introduced in House"},
    "01": {"chamber": "SENATE", "action_desc": "Reported to Senate amended"},
    "02": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 1st committee reporting"},
    "03": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 2nd committee reporting"},
    "04": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 3rd committee reporting"},
    "05": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 4th committee reporting"},
    "06": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 5th committee reporting"},
    "07": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 6th committee reporting"},
    "08": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 7th committee reporting"},
    "09": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 8th committee reporting"},
    "10": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 9th committee reporting"},
    "11": {"chamber": "SENATE", "action_desc": "Reported to Senate amended, 10th committee reporting"},
    "12": {"chamber": "SENATE", "action_desc": "Reported to Senate without amendment, 1st committee reporting"},
    "13": {"chamber": "SENATE", "action_desc": "Reported to Senate without amendment, 2nd committee reporting"},
    "14": {"chamber": "SENATE", "action_desc": "Reported to Senate without amendment, 3rd committee reporting"},
    "15": {"chamber": "SENATE", "action_desc": "Reported to Senate without amendment, 4th committee reporting"},
    "16": {"chamber": "SENATE", "action_desc": "Reported to Senate without amendment, 5th committee reporting"},
    "17": {"chamber": "HOUSE", "action_desc": "Reported to House amended"},
    "18": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part I"},
    "19": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part II"},
    "20": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part III"},
    "21": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part IV"},
    "22": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part V"},
    "23": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part VI"},
    "24": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part VII"},
    "25": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part VIII"},
    "26": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part IX"},
    "27": {"chamber": "HOUSE", "action_desc": "Reported to House amended, Part X"},
    "28": {"chamber": "HOUSE", "action_desc": "Reported to House without amendment, Part I"},
    "29": {"chamber": "HOUSE", "action_desc": "Reported to House without amendment, Part II"},
    "30": {"chamber": "HOUSE", "action_desc": "Reported to House without amendment, Part III"},
    "31": {"chamber": "HOUSE", "action_desc": "Reported to House without amendment, Part IV"},
    "32": {"chamber": "HOUSE", "action_desc": "Reported to House without amendment, Part V"},
    "33": {"chamber": "HOUSE", "action_desc": "Laid on table in House"},
    "34": {"chamber": "SENATE", "action_desc": "Indefinitely postponed in Senate"},
    "35": {"chamber": "SENATE", "action_desc": "Passed Senate amended"},
    "36": {"chamber": "HOUSE", "action_desc": "Passed House amended"},
    "37": {"chamber": "SENATE", "action_desc": "Failed of passage in Senate"},
    "38": {"chamber": "HOUSE", "action_desc": "Failed of passage in House"},
    "39": {"chamber": "HOUSE", "action_desc": "Senate agreed to House amendment with amendment"},
    "40": {"chamber": "SENATE", "action_desc": "House agreed to Senate amendment with amendment"},
    "41": {"chamber": "HOUSE", "action_desc": "Senate disagreed to House amendment with amendment"},
    "42": {"chamber": "SENATE", "action_desc": "House disagreed to Senate amendment with amendment"},
    "43": {"chamber": "HOUSE", "action_desc": "Senate disagreed to House amendment"},
    "44": {"chamber": "SENATE", "action_desc": "House disagreed to Senate amendment"},
    "45": {"chamber": "SENATE", "action_desc": "Senate receded and concurred with amendment"},
    "46": {"chamber": "HOUSE", "action_desc": "House receded and concurred with amendment"},
    "47": {"chamber": "SENATE", "action_desc": "Conference report filed in Senate"},
    "48": {"chamber": "HOUSE", "action_desc": "Conference report filed in House"},
    "49": {"chamber": "BOTH", "action_desc": "Public Law"},
    "50": {"chamber": "BOTH", "action_desc": "Private Law"},
    "51": {"chamber": "BOTH", "action_desc": "Line item veto by President"},
    "52": {"chamber": "SENATE", "action_desc": "Passed Senate amended, 2nd occurrence"},
    "53": {"chamber": "SENATE", "action_desc": "Passed Senate amended, 3rd occurrence"},
    "54": {"chamber": "HOUSE", "action_desc": "Passed House amended, 2nd occurrence"},
    "55": {"chamber": "HOUSE", "action_desc": "Passed House amended, 3rd occurrence"},
    "56": {"chamber": "SENATE", "action_desc": "Senate vitiated passage of bill after amendment"},
    "57": {"chamber": "HOUSE", "action_desc": "House vitiated passage of bill after amendment"},
    "58": {"chamber": "SENATE", "action_desc": "Motion to recommit bill as amended in Senate"},
    "59": {"chamber": "HOUSE", "action_desc": "Motion to recommit bill as amended in House"},
    "60": {"chamber": "SENATE", "action_desc": "Senate agreed to House amendment with amendment, 2nd occurrence"},
    "61": {"chamber": "SENATE", "action_desc": "Senate agreed to House amendment with amendment, 3rd occurrence"},
    "62": {"chamber": "HOUSE", "action_desc": "House agreed to Senate amendment with amendment, 2nd occurrence"},
    "63": {"chamber": "HOUSE", "action_desc": "House agreed to Senate amendment with amendment, 3rd occurrence"},
    "64": {"chamber": "SENATE", "action_desc": "Senate receded and concurred with amendment, 2nd occurrence"},
    "65": {"chamber": "SENATE", "action_desc": "Senate receded and concurred with amendment, 3rd occurrence"},
    "66": {"chamber": "HOUSE", "action_desc": "House receded and concurred with amendment, 2nd occurrence"},
    "67": {"chamber": "HOUSE", "action_desc": "House receded and concurred with amendment, 3rd occurrence"},
    "70": {"chamber": "HOUSE", "action_desc": "Hearing scheduled in House"},
    "71": {"chamber": "SENATE", "action_desc": "Hearing scheduled in Senate"},
    "72": {"chamber": "HOUSE", "action_desc": "Hearing held in House"},
    "73": {"chamber": "SENATE", "action_desc": "Hearing held in Senate"},
    "74": {"chamber": "HOUSE", "action_desc": "Markup in House"},
    "75": {"chamber": "SENATE", "action_desc": "Markup in Senate"},
    "76": {"chamber": "HOUSE", "action_desc": "Rule reported to House"},
    "77": {"chamber": "HOUSE", "action_desc": "Discharged from House committee"},
    "78": {"chamber": "SENATE", "action_desc": "Discharged from Senate committee"},
    "79": {"chamber": "HOUSE", "action_desc": "Reported to House, without amendment"},
    "80": {"chamber": "SENATE", "action_desc": "Reported to Senate without amendment"},
    "81": {"chamber": "HOUSE", "action_desc": "Passed House, without amendment"},
    "82": {"chamber": "SENATE", "action_desc": "Passed Senate, without amendment"},
    "83": {"chamber": "SENATE", "action_desc": "Conference report filed in Senate, 2nd conference report"},
    "84": {"chamber": "SENATE", "action_desc": "Conference report filed in Senate, 3rd conference report"},
    "85": {"chamber": "SENATE", "action_desc": "Conference report filed in Senate, 4th conference report"},
    "86": {"chamber": "HOUSE", "action_desc": "Conference report filed in House, 2nd conference report"},
    "87": {"chamber": "HOUSE", "action_desc": "Conference report filed in House, 3rd conference report"},
    "88": {"chamber": "HOUSE", "action_desc": "Conference report filed in House, 4th conference report"}
}

