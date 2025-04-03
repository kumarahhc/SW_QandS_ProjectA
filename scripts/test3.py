import json
from llama_cpp import Llama
import re

def analyze_security_risk(user_input):
    """
    Runs the Llama.cpp model using llama-cpp-python to analyze security risk.
    This function generates a response in the required JSON format.
    """
    model_path = "OpenO1-LLama-8B-v0.1.Q6_K.gguf"
    llm = Llama(model_path=model_path, n_ctx=512)  # Load the model
    
    # Define the prompt with explicit instructions for JSON format
    prompt = f"""
    You are an assistant specialized in security risk analysis.
    Your task is to determine if the given user message contains a security threat.

    IMPORTANT: Your response MUST be a valid JSON array following this format:

    [
        {{
            "Extended": "[Extended description]",
            "Short": "[Vulnerability Present: YES/NO/MORE]",
            "Details": "[Vulnerability Description]",
            "RiskID": "[Risk ID]",
            "RiskDesc": "[Risk Description]",
            "VulnID": "[Vulnerability ID]",
            "VulnDesc": "[Vulnerability Description]",
            "RiskType": "[Reale/Potenziale]"
        }}
    ]

    You must never add extra text before or after the JSON.
    If no vulnerabilities are found, return:

    []

    Scenario:
    '{user_input}'

    """
    
    output = llm(prompt, max_tokens=512, temperature=0, repeat_penalty=1.2)  # Generate response
    
    # Print the raw output from the model for debugging
    print("Model raw output:", output["choices"][0]["text"])

    # Clean the output by removing any non-JSON text
    raw_output = output["choices"][0]["text"].strip()

    # Manually extract JSON from the output using regex
    json_cleaned_output = re.search(r"\[.*\]", raw_output, re.DOTALL)
    
    if json_cleaned_output:
        # Clean the output to ensure it's a valid JSON array
        raw_json = json_cleaned_output.group().strip()
        
        # Remove unwanted text like '[Output]' from the start and any other non-JSON elements
        cleaned_json = re.sub(r"\[Output\]|\n|<.*?>|\[END OF OUTPUT\]", "", raw_json).strip()
        
        print("Cleaned JSON:", cleaned_json)

        try:
            # Try parsing the cleaned JSON
            json_output = json.loads(cleaned_json)
            return json_output
        except json.JSONDecodeError as e:
            return {"error": f"Model produced invalid JSON: {e}"}
    else:
        return {"error": "No valid JSON found in the output"}

def InteractiveResult():
    while True:
        user_input = input("\nEnter a risk scenario (User Messagee): ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        analysis_result = analyze_security_risk(user_input)
        print(json.dumps(analysis_result, indent=4))

# Example usage
if __name__ == "__main__":
    #user_input = "The Restricted Areas are protected by appropriate security measures (such as, for example, armoured doors, anti-intrusion alarm systems, safes and security containers for the storage of classified information)."
      # Adjust to your model path
    InteractiveResult()
