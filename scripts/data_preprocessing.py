import pandas as pd
from faker import Faker
import os

# Initialize Faker for anonymization
fake = Faker()

# Load the Excel file with multiple sheets
file_path = "../Scenarios.xlsx"

# List all sheet names
excel_file = pd.ExcelFile(file_path)
sheet_names = excel_file.sheet_names
print("Available sheets:", sheet_names)

# Normalize sheet names by stripping leading/trailing spaces
normalized_sheet_names = [name.strip() for name in sheet_names]

# Define target sheet names
target_sheets = ["Examples", "Threats", "Vulnerability"]

# Map target sheet names to their actual names in the file
sheet_mapping = {}
for target_name in target_sheets:
    if target_name in normalized_sheet_names:
        index = normalized_sheet_names.index(target_name)
        sheet_mapping[target_name] = sheet_names[index]
    else:
        raise ValueError(f"Sheet '{target_name}' not found in the Excel file.")

# Read data from the correct sheet names
scenarios_df = pd.read_excel(file_path, sheet_name=sheet_mapping["Examples"])
threats_df = pd.read_excel(file_path, sheet_name=sheet_mapping["Threats"])
vulnerabilities_df = pd.read_excel(file_path, sheet_name=sheet_mapping["Vulnerability"])

# Normalize column names by stripping leading/trailing spaces and converting to lowercase
scenarios_df.columns = [col.strip().lower() for col in scenarios_df.columns]

# Debugging: Print normalized column names
print("Normalized columns in 'Examples' sheet:", scenarios_df.columns)

# Function to anonymize text
def anonymize_text(text):
    # Replace sensitive terms with placeholders
    anonymized = text
    if "Company" in str(text):  # Ensure text is converted to string
        anonymized = anonymized.replace("Company", fake.company())
    if "System" in str(text):
        anonymized = anonymized.replace("System", fake.word(ext_word_list=["Platform", "Application", "Service"]))
    return anonymized

# Apply anonymization to the 'User' column in Scenarios worksheet
if 'user' in scenarios_df.columns:
    scenarios_df['user'] = scenarios_df['user'].apply(anonymize_text)
else:
    print("Warning: 'User' column not found in the 'Examples' sheet.")


# Create the 'data' directory if it doesn't exist
output_dir = "../data"
os.makedirs(output_dir, exist_ok=True)  # Creates the directory if it doesn't exist

# Save the anonymized data to a new Excel file
output_file = os.path.join(output_dir, "anonymized_scenarios.xlsx")
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    scenarios_df.to_excel(writer, sheet_name="Examples", index=False)
    threats_df.to_excel(writer, sheet_name="Threats", index=False)
    vulnerabilities_df.to_excel(writer, sheet_name="Vulnerability", index=False)

print(f"Anonymized data saved to {output_file}")