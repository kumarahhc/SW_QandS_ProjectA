from llama_cpp import Llama
import json
import re

# Initialize the model with optimized settings
llm = Llama(
    model_path="llama-2-7b-chat.Q6_K.gguf",
    chat_format="llama-2",  # Required for Llama-2 chat models
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=0  # Force CPU-only mode
)

def analyze_security(scenario: str,rag: bool = False) -> dict:
    """Analyze security scenario and return structured JSON"""
    messages = [
        {
            "role": "system", 
            "content": """You are a cybersecurity expert. Return ONLY valid JSON with these EXACT fields:
            {
                "Extended": "detailed risk description",
                "Short": "YES/NO/MORE",
                "Details": "specific vulnerability details",
                "RiskID": "risk identifier (e.g., AUTH-001)",
                "RiskDesc": "risk impact description",
                "VulnID": "standard ID (e.g., CWE-287)",
                "VulnDesc": "vulnerability type",
                "RiskType": "Real/Potential"
            }"""
        },
        {
            "role": "user", 
            "content": f"""Analyze this scenario and fill the JSON with ACTUAL VALUES:
            Example for 'Unencrypted database':
            {{
                "Extended": "Database lacks encryption exposing PII",
                "Short": "YES",
                "Details": "No TLS or at-rest encryption",
                "RiskID": "DB-001",
                "RiskDesc": "Data breach risk",
                "VulnID": "CWE-311",
                "VulnDesc": "Missing Encryption",
                "RiskType": "Real"
            }}
            
            Current Scenario: {scenario}"""
        }
    ]
    
    response = llm.create_chat_completion(
        messages=messages,
        temperature=0.1,  # Low for deterministic output
        max_tokens=512,
        stop=["}\n"]  # Stop after complete JSON object
    )
    
    # Extract and clean JSON
    return response['choices'][0]['message']['content']

def parse_output(raw: str) -> dict:
    """Extract JSON from model output"""
    try:
        json_str = re.search(r"\{.*\}", raw, re.DOTALL).group()
        return json.loads(json_str)
    except Exception:
        print(f"! Failed to parse JSON from:\n{raw}")
        return {"error": "Invalid output format"}

def interactive_analysis(rag_enabled: bool = False):
    print("\n🔍 Security Risk Analyzer (LLaMA-2 7B)")
    print(f"Mode: {'RAG Enabled' if rag_enabled else 'Base Model'}")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            user_input = input("Enter risk scenario: ").strip()
            if user_input.lower() in ("exit", "quit"):
                break
                
            if not user_input:
                print("! Please enter a scenario")
                continue
                
            print("\nAnalyzing...")
            result = analyze_security(user_input, rag_enabled)
            print(json.dumps(result, indent=2))
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        
# Test with your scenario
interactive_analysis(rag_enabled=False)


#test_case = "User authentication is not properly implemented"
#result = analyze_security(test_case)
#print(json.dumps(result, indent=2))

# Expected Output Example:
# {
#   "Extended": "Improper authentication allows bypassing login controls",
#   "Short": "YES",
#   "Details": "Missing multi-factor authentication",
#   "RiskID": "AUTH-001",
#   "RiskDesc": "Unauthorized access risk",
#   "VulnID": "CWE-287",
#   "VulnDesc": "Improper Authentication",
#   "RiskType": "Real"
# }