import os
import shutil
from backend.utils.keywords import keywords  # Importing the keywords list

def keyword_search_in_file(file_path, keywords):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        for keyword in keywords:
            if keyword.lower() in content.lower():
                return True
    return False

def move_files_based_on_keywords(source_directory, target_directory, keywords):
    for root, _, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                if keyword_search_in_file(file_path, keywords):
                    shutil.move(file_path, os.path.join(target_directory, file))
                    print(f"Moved file: {file}")

def main():
    source_directory = 'backend/data/fullBill_xml_files'
    target_directory = 'backend/data/related_fullBill_xml_files'

    move_files_based_on_keywords(source_directory, target_directory, keywords)

if __name__ == "__main__":
    main()