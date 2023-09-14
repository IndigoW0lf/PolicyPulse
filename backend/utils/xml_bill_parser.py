def parse_bill(tree):
    # Parse the bill data from the XML tree.
    bill_data = {
        'number': get_text(tree, './/bill/number'),
        'updateDate': get_text(tree, './/bill/updateDate'),
        'originChamber': get_text(tree, './/bill/originChamber'),
        'type': get_text(tree, './/bill/type'),
        'introducedDate': get_text(tree, './/bill/introducedDate'),
        'congress': get_text(tree, './/bill/congress'),
        'display_title': get_display_title(tree),
        'official_title': get_official_title(tree),
        'summaries': parse_summaries(tree),
        'fullBillTexts': parse_fullBillTexts(tree),
        'subjects': parse_subjects(tree),
        "textVersions": parse_text_versions(tree),
        "latestAction": parse_latest_action(tree),
        "titles": parse_titles(tree),
        "committees": parse_committees(tree),
        "sponsors": parse_sponsors(tree),
        "vetoMessages": parse_veto_messages(tree),
        "policyAreas": parse_policyAreas(tree),
        "relatedBills": parse_relatedBills(tree),
        "coSponsors": parse_coSponsors(tree),
        "fullBillTexts": parse_fullBillTexts(tree),
        "actions": parse_actions(tree),
        "amendments": parse_amendments(tree),
    }
    return bill_data

def get_text(tree, xpath):
    elements = tree.xpath(xpath)
    if elements:
        if len(elements) == 1:
            return elements[0].text
        else:
            return [element.text for element in elements]
    else:
        return None

def get_display_title(tree):
    title_element = tree.find(".//bill/titles/item[titleType='Display Title']")
    return title_element.text if title_element is not None else ""

def get_official_title(tree):
    title_element = tree.find(".//bill/titles/item[titleType='Official Title as Introduced']")
    return title_element.text if title_element is not None else ""

def get_text(element, tag):
    """Helper function to get the text of a child element with the given tag."""
    child = element.find(tag)
    return child.text if child is not None else None

def parse_actions(tree):
    """Parse the actions section of the bill data."""
    actions = tree.findall(".//bill/actions/item")
    return [
        {
            "actionDate": get_text(action, "actionDate"),
            "actionTime": get_text(action, "actionTime"),
            "committee": {
                "name": get_text(action, "committee/name"),
            },
            "text": get_text(action, "text"),
            "type": get_text(action, "type"),
            "actionCode": get_text(action, "actionCode"),
            "sourceSystem": {
                "code": get_text(action, "sourceSystem/code"),
                "name": get_text(action, "sourceSystem/name"),
            }
        }
        for action in actions
    ]

def parse_amendments(tree):
    """Parse the amendments section of the bill data."""
    amendments = tree.findall(".//bill/amendments/item")
    return [
        {
            "amendment_number": get_text(amendment, "amendment_number"),
            "description": get_text(amendment, "description"),
            "date_proposed": get_text(amendment, "date_proposed"),
            "status": get_text(amendment, "status"),
        }
        for amendment in amendments
    ]

def parse_committees(tree):
    """Parse the committees section of the bill data."""
    committees = tree.findall(".//bill/committees/item")
    return [
        {
            "name": get_text(committee, "name"),
            "chamber": get_text(committee, "chamber"),
            "committee_code": get_text(committee, "committee_code"),
        }
        for committee in committees
    ]

def parse_coSponsors(tree):
    """Parse the co-sponsors section of the bill data."""
    co_sponsors = tree.findall(".//bill/coSponsors/item")
    return [
        {
            "politician_id": get_text(co_sponsor, "politician_id"),
            "bill_id": get_text(co_sponsor, "bill_id"),
        }
        for co_sponsor in co_sponsors
    ]

def parse_fullBillTexts(tree):
    """Parse the full bill texts section of the bill data."""
    full_bill_texts = tree.findall(".//bill/fullBillTexts/item")
    return [
        {
            "title": get_text(full_bill_text, "title"),
            "bill_metadata": get_text(full_bill_text, "bill_metadata"),
            "actions": get_text(full_bill_text, "actions"),
            "sections": get_text(full_bill_text, "sections"),
        }
        for full_bill_text in full_bill_texts
    ]

def parse_latest_action(tree):
    """Parse the latest action section of the bill data."""
    return {
        "actionDate": get_text(tree, ".//bill/latestAction/actionDate"),
        "text": get_text(tree, ".//bill/latestAction/text"),
        "actionTime": get_text(tree, ".//bill/latestAction/actionTime"),
    }

def parse_policyAreas(tree):
    """Parse the policy areas section of the bill data."""
    policy_areas = tree.findall(".//bill/policyAreas/item")
    return [
        {
            "name": get_text(policy_area, "name"),
            "description": get_text(policy_area, "description"),
        }
        for policy_area in policy_areas
    ]

def parse_relatedBills(tree):
    """Parse the related bills section of the bill data."""
    related_bills = tree.findall(".//bill/relatedBills/item")
    return [
        {
            "bill_id": get_text(related_bill, "bill_id"),
            "related_bill_id": get_text(related_bill, "related_bill_id"),
        }
        for related_bill in related_bills
    ]

def parse_sponsors(tree):
    """Parse the sponsors and cosponsors section of the bill data."""
    sponsors = tree.findall(".//bill/sponsors/item") + tree.findall(".//bill/cosponsors/item")
    return [
        {
            "bioguide_id": get_text(sponsor, "bioguideId"),
            "first_name": get_text(sponsor, "firstName"),
            "middle_name": get_text(sponsor, "middleName"),
            "last_name": get_text(sponsor, "lastName"),
            "name": " ".join(filter(None, [get_text(sponsor, "firstName"), get_text(sponsor, "middleName"), get_text(sponsor, "lastName")])),  # Combining first, middle and last names
            "party": get_text(sponsor, "party"),
            "state": get_text(sponsor, "state"),
        }
        for sponsor in sponsors
    ]


def parse_subjects(tree):
    """Parse the subjects section of the bill data."""
    return {
        'legislativeSubjects': [
            {'name': get_text(subject, 'name')}
            for subject in tree.xpath('.//bill/subjects/legislativeSubjects/item')
        ],
        'billSubjects': [
            {'name': get_text(subject, 'name')}
            for subject in tree.xpath('.//bill/subjects/billSubjects/item')
        ],
        'otherSubjects': [
            {
                'name': get_text(subject, 'name'),
                'parentSubject': {'name': get_text(subject, 'parentSubject/name')}
            }
            for subject in tree.xpath('.//bill/subjects/otherSubjects/item')
        ],
        'primarySubjects': [
            {
                'name': get_text(subject, 'name'),
                'parentSubject': {'name': get_text(subject, 'parentSubject/name')}
            }
            for subject in tree.xpath('.//bill/subjects/primarySubjects/item')
        ]
    }

def parse_summaries(tree):
    """Parse the summaries section of the bill data."""
    summaries = tree.findall(".//bill/summaries/summary")
    versions = [
        {
            "version_code": get_text(summary, "versionCode"),
            "action_date": get_text(summary, "actionDate"),
            "action_desc": get_text(summary, "actionDesc"),
            "update_date": get_text(summary, "updateDate"),
            "text": get_text(summary, "text"),
        }
        for summary in summaries
    ]
    return {"versions": versions}


def parse_titles(tree):
    """Parse the titles section of the bill data."""
    titles = tree.findall(".//bill/titles/item")
    for title in titles:
        title_type = get_text(title, "titleType")
        if title_type == "Official Title as Introduced":
            return get_text(title, "title")
    return ""  # Return an empty string if no matching title is found

def parse_text_versions(tree):
    """Parse the text versions section of the bill data."""
    text_versions = tree.findall(".//bill/textVersions/item")
    return [
        {
            "type": get_text(version, "type"),
            "date": get_text(version, "date"),
            "url": get_text(version, "formats/item/url"),
        }
        for version in text_versions
    ]

def parse_veto_messages(tree):
    """Parse the veto messages section of the bill data."""
    veto_messages = tree.findall(".//bill/vetoMessages/item")
    return [
        {
            "date": get_text(veto_message, "date"),
            "message": get_text(veto_message, "message"),
            "president": get_text(veto_message, "president"),
            "text": get_text(veto_message, "text"),
        }
        for veto_message in veto_messages
    ]