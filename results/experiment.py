import pandas as pd
import re
from model_integration import generate_response
from scripts.testing.rag_setup import setup_rag, get_rag_prompt

# Initialize RAG
db = setup_rag()

def test_single_scenario(description):
    # Generate RAG-augmented prompt
    rag_prompt = get_rag_prompt(description, db)
    
    # Generate response from LLaMA-O1
    response = generate_response(rag_prompt)
    print("\nAI Response:")
    print(response)
    
    # Parse output (example logic)
    threats = re.findall(r"Threat: (M\d+)", response)
    vulnerabilities = re.findall(r"Vulnerability: (V\d+)", response)
    classification = "Real" if "Real" in response else "Potential"
    
    # Return structured output
    return {
        "reasoning": response,
        "classification": classification,
        "threats": threats,
        "vulnerabilities": vulnerabilities
    }

if __name__ == "__main__":
    # Manually input a scenario
    user_input = input("Enter a risk scenario (or type 'exit' to quit): ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Exiting...")
    else:
        result = test_single_scenario(user_input)
        print("\nStructured Output:")
        print(result)