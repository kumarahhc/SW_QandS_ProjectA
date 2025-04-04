import json
import re

def extract_json_from_raw_output(raw_output):
    # Print the raw output to examine the issue
    print("Raw Output:", raw_output)

    # First, remove everything before the first '[' and after the last ']'
    json_cleaned_output = re.search(r"\[.*\]", raw_output, re.DOTALL)
    
    if json_cleaned_output:
        # Clean the output to ensure it's a valid JSON array
        raw_json = json_cleaned_output.group().strip()
        
        # Remove unwanted text like '[Output]' from the start and any other non-JSON elements
        cleaned_json = re.sub(r"\[Output\]|\n|<.*?>", "", raw_json).strip()
        
        print("Cleaned JSON:", cleaned_json)

        try:
            # Try parsing the cleaned JSON
            json_output = json.loads(cleaned_json)
            return json_output
        except json.JSONDecodeError as e:
            return {"error": f"Model produced invalid JSON: {e}"}
    else:
        return {"error": "No valid JSON found in the output"}

# Raw output from the model (adjust this to what you get from the model)
raw_output = """
Threat M5 (Data leakage): Unauthorized disclosure of data, which can occur through various channels such as network traffic or storage media.
Threat M7 (Session hijacking): Attack where the attacker gains unauthorized access to a user's session by capturing their cookies.

Given that application logs are recorded, analyze if there is any security threat present in this scenario.

[Output]
[
    {
        "Extended": "Recording of application logs can lead to data leakage as sensitive information may be stored or transmitted insecurely.",
        "Short": "Vulnerability Present: YES",
        "Details": "The act of recording application logs without proper security measures allows potential attackers to intercept and exploit the recorded data, leading to unauthorized disclosure of sensitive information. This could include user credentials, transaction details, or other confidential data that if exposed can compromise system integrity.",
        "RiskID": "M5",
        "RiskDesc": "Data Leakage",
        "VulnID": "DL-001",
        "VulnDesc": "Insecure storage and transmission of application logs resulting in unauthorized disclosure of sensitive information.",
        "RiskType": "Potenziale"
    }
]

<Thought
"""

# Extract and parse the JSON data
json_result = extract_json_from_raw_output(raw_output)

# Print the result
print(json.dumps(json_result, indent=4))
