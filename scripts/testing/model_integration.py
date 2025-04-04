from llama_cpp import Llama
from scripts.testing.rag_setup import setup_rag, get_rag_prompt
import re

# Load the GGUF model
model_path = "llama-O1-Supervised-1129-q4_k_m.gguf"
llm = Llama(model_path=model_path)

def generate_response(prompt, max_tokens=256):
    """Generate a response from the LLaMA-O1 model."""
    response = llm(prompt, max_tokens=max_tokens)
    return response["choices"][0]["text"]

def parse_output(response):
    """Parse the model's output into a structured format."""
    threats = re.findall(r"M\d+", response)
    vulnerabilities = re.findall(r"V\d+", response)
    classification = "Real" if "Real" in response else "Potential"
    
    return {
        "reasoning": response.strip(),
        "classification": classification,
        "threats": threats,
        "vulnerabilities": vulnerabilities
    }

if __name__ == "__main__":
    # Set up RAG
    db = setup_rag()
    
    print("LLaMA-O1 Model Ready for Risk Analysis!")
    while True:
        user_input = input("Enter a risk scenario (or type 'exit' to quit): ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Exiting...")
            break
        
        # Create a structured prompt
        structured_prompt = f"""
        Analyze this risk scenario using PCM-ANS TI-002 standards:
        '{user_input}'

        Follow this structure:
        1. Identify threats (e.g., M1 - Queuing Access)
        2. Link vulnerabilities (e.g., V7 - Untested software)
        3. Classify risk type (Real/Potential)
        4. Propose mitigations (e.g., ISO 27001 controls)
        """
        
        # Generate RAG-augmented prompt
        rag_prompt = get_rag_prompt(structured_prompt, db)
        
        # Generate response
        response = generate_response(rag_prompt)
        print("\nAI Response:")
        print(response)
        
        # Parse the output
        parsed_output = parse_output(response)
        print("\nParsed Output:")
        print(parsed_output)