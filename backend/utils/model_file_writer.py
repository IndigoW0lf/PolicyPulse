import os

# Step 1: Identify all the files that contain your SQLAlchemy models
model_files = [
    "backend/database/models/action_type.py",
    "backend/database/models/action.py",
    "backend/database/models/amendment.py",
    "backend/database/models/bill_full_text.py",
    "backend/database/models/bill_title.py",
    "backend/database/models/bill.py",
    "backend/database/models/co_sponsor.py",
    "backend/database/models/committee.py",
    "backend/database/models/law.py",
    "backend/database/models/loc_summary.py",
    "backend/database/models/note.py",
    "backend/database/models/policy_area.py",
    "backend/database/models/politician.py",
    "backend/database/models/recorded_vote.py",
    "backend/database/models/related_bill.py",
    "backend/database/models/subject.py",
]

output_file_path = "backend/data/model_file.py"

# Step 2: For each file, read its content and separate import statements and other lines
import_statements = set()
other_lines = []

for model_file in model_files:
    with open(model_file, 'r') as file:
        lines = file.readlines()
        
        in_repr_method = False
        in_to_dict_method = False
        for line in lines:
            # Check if we are inside a __repr__ or to_dict method definition
            if 'def __repr__' in line:
                in_repr_method = True
            elif 'def to_dict(self):' in line:
                in_to_dict_method = True
            elif in_repr_method and line.strip() == '':
                # We assume that there's an empty line after the end of the __repr__ method
                in_repr_method = False
            elif in_to_dict_method and line.strip() == '':
                # We assume that there's an empty line after the end of the to_dict method
                in_to_dict_method = False
            elif not in_repr_method and not in_to_dict_method:
                # Separate import statements and other lines
                if line.strip().startswith("from") or line.strip().startswith("import"):
                    import_statements.add(line)
                else:
                    other_lines.append(line)

# Step 3: Write the import statements followed by other lines to the output file
with open(output_file_path, 'w') as output_file:
    for import_statement in import_statements:
        output_file.write(import_statement)
    
    output_file.write("\n")
    
    for line in other_lines:
        output_file.write(line)
