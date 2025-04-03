import pandas as pd
from sklearn.model_selection import train_test_split

# Step 1: Load the anonymized data
file_path = "../data/anonymized_scenarios.xlsx"
scenarios_df = pd.read_excel(file_path, sheet_name="Examples")

# Step 2: Split the data
# Total samples: 1283 (as per the original study)
# Training: 926 samples (135 unique scenarios)
# Validation: 278 samples
# Test: 357 samples (58 unique scenarios)

# First, split into training + validation (648 + 278 = 926) and test (357)
train_val_df, test_df = train_test_split(scenarios_df, test_size=357, random_state=42)

# Then, split training + validation into training (926) and validation (278)
train_df, val_df = train_test_split(train_val_df, test_size=278, random_state=42)

# Step 3: Save the splits to separate files
train_df.to_csv("../data/train_scenarios.csv", index=False)
val_df.to_csv("../data/validation_scenarios.csv", index=False)
test_df.to_csv("../data/test_scenarios.csv", index=False)

print("Data split complete.")
print(f"Training set: {len(train_df)} samples")
print(f"Validation set: {len(val_df)} samples")
print(f"Test set: {len(test_df)} samples")

def saveJsonL(string_data, filename):
    """
    Writes a string to a file and downloads it.

    Args:
        string_data (str): The string data to be written to the file.
        filename (str): The name of the file.

    """
    with open(filename, 'w', encoding=file_encoding) as file:
        file.write(string_data)
    files.download(filename)