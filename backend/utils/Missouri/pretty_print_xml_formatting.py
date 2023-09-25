import os
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

def pretty_print_xml(xml_string):
    try:
        dom = parseString(xml_string)
        return dom.toprettyxml()
    except ExpatError as e:
        return None

def format_xml_files_in_directory(directory_path):
    # List all files in the directory
    files = os.listdir(directory_path)

    for file in files:
        if file.endswith('.xml'):
            file_path = os.path.join(directory_path, file)

            # Read the content of the file
            with open(file_path, 'r') as f:
                content = f.read()

            # Format the content
            formatted_content = pretty_print_xml(content)

            if formatted_content:
                # Write the formatted content back to the file
                with open(file_path, 'w') as f:
                    f.write(formatted_content)
                print(f"Formatted {file_path}")
            else:
                print(f"Error formatting {file_path}. The XML might be malformed.")

directory_path = 'backend/utils/Missouri/MO_Keyword_XMLs'  # Replace with your directory path
format_xml_files_in_directory(directory_path)
