from llama_cpp import Llama
import json
import re
from typing import Union
import pandas as pd

# Initialize the model
llm = Llama(
    model_path="llama-2-7b-chat.Q6_K.gguf",
    chat_format="llama-2",
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=0
)

def analyze_security(scenario: str) -> dict:
    """Strict JSON output generator with format enforcement"""
    template = '''{
        "Extended": "Unencrypted database exposes customer PII",
        "Short": "YES/NO/MORE",
        "Details": "No TLS or at-rest encryption implemented",
        "RiskID": " R-001",
        "RiskDesc": " Data breach risk",
        "VulnID": " V-311",
        "VulnDesc": "Missing Encryption",
        "RiskType": "Real/Potential"
    }'''
    messages = [
        {
            "role": "system",
            "content": f"""You are a JSON generator for security analysis. 
            Return ONLY the JSON output with ACTUAL VALUES - NO EXPLANATIONS.
            
            Current Template (REPLACE ALL VALUES):
            {template}"""
        },
        {
            "role": "user",
            "content": f"Scenario: {scenario}"
        }
    ]
    
    response = llm.create_chat_completion(
        messages=messages,
        temperature=0,
        max_tokens=512,
        stop=["}\n"]
    )
    
    return extract_json(response['choices'][0]['message']['content'])
    """Handle both raw text and pre-parsed JSON outputs"""
def validate_output(output: Union[str, dict]) -> dict:
    """Handle both raw text and pre-parsed JSON outputs"""
    try:
        # Handle both string and dict inputs
        if isinstance(output, str):
            # Remove any non-JSON text
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found")
            result = json.loads(json_match.group())
        else:
            result = output
        
        # Validate flat structure
        required_fields = {
            "Extended": str,
            "Short": str,
            "Details": str,
            "RiskID": str,
            "RiskDesc": str,
            "VulnID": str,
            "VulnDesc": str,
            "RiskType": str
        }
        
        # Check all fields exist and have correct types
        for field, field_type in required_fields.items():
            if field not in result:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(result[field], field_type):
                raise ValueError(f"Field '{field}' must be {field_type.__name__}")
                
        # Check for unwanted nesting
        for value in result.values():
            if isinstance(value, (dict, list)):
                raise ValueError("Nested structures not allowed")
                
        return result
        
    except Exception as e:
        print(f"! Validation error: {e}")
        print(f"Problematic output was:\n{output}")
        return {"error": "Invalid analysis output"}
    
def extract_json(raw: str) -> dict:
    """Extract and validate JSON from raw output"""
    try:
        # Find the first complete JSON object
        start = raw.find('{')
        end = raw.rfind('}') + 1
        json_str = raw[start:end]
        
        # Basic validation
        if not json_str or json_str.count('{') != json_str.count('}'):
            raise ValueError("Invalid JSON structure")
            
        parsed = json.loads(json_str)
        
        # Check required fields
        required = ["Extended", "Short", "Details", "RiskID", 
                   "RiskDesc", "VulnID", "VulnDesc", "RiskType"]
        for field in required:
            if field not in parsed:
                raise ValueError(f"Missing field: {field}")
                
        return parsed
        
    except Exception as e:
        print(f"! Extraction failed: {e}")
        print(f"Raw output was:\n{raw}")
        return {"error": "Invalid output - expected pure JSON"}

def interactive_session():
    print("\n🔒 Security Risk Analyzer")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            scenario = input("Enter security scenario: ").strip()
            if scenario.lower() in ("exit", "quit"):
                break
                
            if not scenario:
                print("! Please enter a scenario")
                continue
                
            print("\nAnalyzing...")
            result = analyze_security(scenario)
            result_json=validate_output(result)
            print(json.dumps(result_json, indent=2))
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nSession ended.")
            break

def runTest(rag):
    if(rag):
        print("RAG Assistant (LLaMA + FAISS Vector DB) is used to geratare result")
    
    test_df=pd.read_csv("../data/test_scenario.csv")
    results = []
    i=1
    for _, row in test_df.iterrows():
        scenario_text=row["User"]
        print(f"analyzing {i} of {test_df.shape[0]}")
        output = analyze_security(scenario_text)
        # Parse Output to JSON
        parsed_data = validate_output(output)
        # Append Results
        results.append({
            "Scenario ID": row["Scenario ID"],
            "User Input": scenario_text,
            "JSON": parsed_data,
            "AI Result":output
        })
        i+=1
    
    # Save Results to JSON File
    with open("../data/test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    interactive_session()
    #runTest(False)