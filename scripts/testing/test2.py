import json
from llama_cpp import Llama
import re

def analyze_security_risk(user_input, model_path):
    """
    Runs the Llama.cpp model using llama-cpp-python to analyze security risk.
    """
    llm = Llama(model_path=model_path, n_ctx=512)  # Load the model
    
    prompt = f"""
    You are an assistant specialized in security risk analysis.
    Your task is to determine if the given user message contains a security threat.

    ⚠️ IMPORTANT: Your response MUST be a valid JSON array following this format:

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

    response_text = output["choices"][0]["text"].strip()

    # Manually extract JSON from the output using regex
    json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
    
    if json_match:
        try:
            json_output = json.loads(json_match.group())  # Parse JSON
            return json_output
        except json.JSONDecodeError:
            return {"error": "Model produced invalid JSON"}
    else:
        return {"error": "No valid JSON found in the output"}

# Example usage
if __name__ == "__main__":
    user_input = "The CIS Application services are managed based on user access rights, identification and assignment of access rights are managed directly by the system users."
    model_path = "llama-O1-Supervised-1129-q4_k_m.gguf"  # Adjust to your model path
    analysis_result = analyze_security_risk(user_input, model_path)
    print(json.dumps(analysis_result, indent=4))
