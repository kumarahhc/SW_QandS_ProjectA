
import json
import pandas as pd
from faker import Faker
from sklearn.model_selection import train_test_split

"""Used to process data before testing"""
# Initialize Faker for anonymization
fake = Faker()

def anonymize_data(file_name):
    df = pd.read_csv(file_name,encoding='cp1252')
    # Apply anonymization to "User" column
    if 'User' in df.columns:
        df['User'] = df['User'].apply(anonymize_text)
    print(df.head())
    return df

def split_data_and_save(df):
    # Step 2: Split the data
    # Total samples: 1283 (as per the original study)
    # Training: 926 samples (135 unique scenarios)
    # Validation: 278 samples
    # Test: 357 samples (58 unique scenarios)
    # First, split into training + validation (648 + 278 = 926) and test (357)
    train_val_df, test_df = train_test_split(df, test_size=357, random_state=42)

    # Then, split training + validation into training (926) and validation (278)
    train_df, val_df = train_test_split(train_val_df, test_size=278, random_state=42)
    
    #save into csv
    train_df.dropna(how="all", inplace=True)
    val_df.dropna(how="all", inplace=True)
    test_df.dropna(how="all", inplace=True)
    
    train_df.to_csv("../data/training_scenario.csv",index=False)
    val_df.to_csv("../data/validation_scenario.csv",index=False)
    test_df.to_csv("../data/test_scenario.csv",index=False)
    convert_to_jsonl(train_df,"../data/training_data.jsonl")
    print("Data split and saved successfully!")

def convert_to_jsonl(df,out_file_name):
    json_data={}
    for index,row in df.iterrows():
        senario_id=df.at[index,"Scenario ID"]
        if(df.at[index,"Assistant - Short"]=="No"):
            assistance_info={
                'Extended':df.at[index,"Assistant - Extended"],
                'Short':df.at[index,"Assistant - Short"]}
        else:
            assistance_info={
                'Extended':df.at[index,"Assistant - Extended"],
                'Short':df.at[index,"Assistant - Short"],
                'Details': df.at[index,'Assistant - Details'],
                'Risk_ID': df.at[index,'Assistant - Risk ID'],
                'Risk_Description': df.at[index,'Assistant - Risk description'],
                'Vln_ID': df.at[index,'Assistant - Vulnerability ID'],
                'Vln_Description': df.at[index,'Assistant - Vulnerability description'],
                'Risk_Type': df.at[index,'Assistant - Risk occurrence type']
                }
        #add row to json
        if(senario_id not in json_data):
            json_data[senario_id]={"User_Message":df.at[index,"User"],"Assistance_infos":[assistance_info]}
        else:
            json_data[senario_id]["Assistance_infos"].append(assistance_info)
    #save jsonl file
    with open(out_file_name,"w",encoding="utf-8") as f:
        for key,value in json_data.items():
            json_line=json.dumps({"Senario ID": key, **value},ensure_ascii=False)
            f.write(json_line+"\n")
        print(f"JSONL file saved to {out_file_name}")
        
# Function to anonymize text
def anonymize_text(text):
    # Replace sensitive terms with placeholders
    anonymized = text
    if "Company" in str(text):  # Ensure text is converted to string
        anonymized = anonymized.replace("Company", fake.company())
    if "System" in str(text):
        anonymized = anonymized.replace("System", fake.word(ext_word_list=["Platform", "Application", "Service"]))
    return anonymized

if __name__ == "__main__":
    df=anonymize_data("../data/Scenarios.csv")
    split_data_and_save(df)