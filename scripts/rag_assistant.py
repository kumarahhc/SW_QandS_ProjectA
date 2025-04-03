import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama
import re
import pandas as pd
import json

# Load Vector DB and metadata
index = faiss.read_index("vector_db.index")
with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# Embedding Model (same one used in indexing)
embed_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Load LLaMA Model
#llm = Llama(model_path="llama-O1-Supervised-1129-q4_k_m.gguf")
llm = Llama(model_path="OpenO1-LLama-8B-v0.1.Q6_K.gguf", n_ctx=512)

#llm = Llama(model_path="LLaMA-O1-Supervised-1129.Q8_0.gguf")
#llm = Llama(model_path="llama-2-7b.Q4_K_M.gguf", verbose=True)

def retrieve_context(query, top_k=2):
    """Search relevant vulnerability & risk chunks."""
    query_vec = embed_model.encode([query])
    D, I = index.search(np.array(query_vec), top_k)
    results = [metadata[i] for i in I[0]]

    context = ""
    for r in results:
        if r["type"] == "vulnerability":
            context += f"\nVulnerability {r['id']} ({r['title']}): {r['description']}"
        else:
            context += f"\nThreat {r['id']} ({r['title']}): {r['description']}"
    return context

def generate_response(prompt):
    """Generate LLaMA model output."""
    #response = llm(prompt, max_tokens=max_tokens,repeat_penalty=1.2, temperature=0,stop=["\n"])
    response = llm(prompt, max_tokens=512, temperature=0, repeat_penalty=1.2) 
    return response["choices"][0]["text"].strip()

def parse_output(response):
    """Parse the model's output into structured data."""
    json_cleaned_output = re.search(r"\[.*\]", response, re.DOTALL)
    
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

        # Step 1: Retrieve relevant vulnerabilities & risks
        context = retrieve_context(user_input)

        # Step 2: Compose full prompt
        structured_prompt = f"""
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

        print("\n Prompt:")
        print(structured_prompt)
        
        # Step 3: Get response from LLaMA
        output = generate_response(structured_prompt)
        print("\n AI Response:")
        print(output)

        # Step 4: Parse and display structured output
        parsed = parse_output(output)
        print("\n Parsed Output:")
        print(parsed)

def main():
    print("RAG Assistant Ready (LLaMA + FAISS Vector DB)")
    test_df=pd.read_csv("../data/test_scenario.csv")
    results = []
    for _, row in test_df.iterrows():
        scenario_text=row["User"]
        # Retrieve Relevant Context
        context = retrieve_context(scenario_text)
        
        # Construct Prompt for LLaMA
        
        structured_prompt = f"""
        You are an assistant in security risk analysis.
        Analyze the following risk scenario:

        Scenario:
        '{scenario_text}'

        correlate information:
        {context}

        Follow this structure:
        1. Identify threats (e.g., M1 - Queuing Access)
        2. Link vulnerabilities (e.g., V7 - Untested software)
        3. Classify risk type (Real/Potential)
        4. Propose mitigations (e.g., ISO 27001 controls)
        [
            {{
                "Extended": "[Descrizione estesa]",
                "Short": "[YES/NO/MORE]",
                "Details": "[Descrizione della vulnerabilità]",
                "RiskID": "[ID Rischio]",
                "RiskDesc": "[Descrizione del rischio]",
                "VulnID": "[ID Vulnerabilità]",
                "VulnDesc": "[Descrizione della vulnerabilità]",
                "RiskType": "[Reale/Potenziale]"
            }}
        ]
        Respond **ONLY** in JSON format.
        """
        # Generate AI Response
        structured_prompt = structured_prompt[:400]
        output = generate_response(structured_prompt)
        # Parse Output
        parsed_data = parse_output(output)
        # Append Results
        results.append({
            "Scenario ID": row["Scenario ID"],
            "User Input": scenario_text,
            "AI Response": parsed_data
        })
        
    # Save Results to JSON File
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    #main()
    InteractiveResult()
