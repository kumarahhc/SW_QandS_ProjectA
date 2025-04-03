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

# Load DevQuasar model
llm = Llama(model_path="O1-OPEN.OpenO1-Qwen-7B-v0.1.Q5_K_M.gguf")

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

def generate_response(prompt, max_tokens=256):
    """Generate response using the DevQuasar model."""
    response = llm(prompt, max_tokens=max_tokens, temperature=0.7, stop=["\n"])
    return response["choices"][0]["text"]

def parse_output(response):
    """Parse the model's output into structured data."""
    threats = re.findall(r"M\d+\s\([^)]+\)", response)
    vulnerabilities = re.findall(r"V\d+\s\([^)]+\)", response)
    classification = "Real" if "real risk" in response.lower() else "Potential"
    
    parsed_results = []
    for threat in threats:
        threat_id, threat_desc = re.match(r"(M\d+)\s\((.+?)\)", threat).groups()
        for vuln in vulnerabilities:
            vuln_id, vuln_desc = re.match(r"(V\d+)\s\((.+?)\)", vuln).groups()
            parsed_results.append({
                "Extended": response.strip(),
                "Short": "yes",
                "Details": f"{threat_desc} is linked to {vuln_desc}",
                "RiskID": threat_id,
                "RiskDesc": threat_desc,
                "VulnID": vuln_id,
                "VulnDesc": vuln_desc,
                "RiskType": classification
            })
    return parsed_results if parsed_results else [{"Short": "no"}]

def InteractiveResult():
    while True:
        user_input = input("\nEnter a risk scenario (User Message): ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        context = retrieve_context(user_input)
        structured_prompt = f"""
        You are an assistant in security risk analysis.
        You need to determine if the current user message contains a security threat.
        If a security threat is present, please explain what the security threat is.
        You must reply with "more" in the "Short" field if you think additional details should be provided along with the vulnerability already discovered.
        You must reply with "no" in the "Short" field if you think NO vulnerabilities are present.
        You must reply with "yes" in the "Short" field if you think there is at least one vulnerability.
        You must NEVER HALLUCINATE.

        Always respond with an array of valid JSON output. For each vulnerability you find, create an item as follows:
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
        Respond **ONLY** in JSON format.

        Scenario:
        '{user_input}'

        Relevant Information:
        {context}
        """
        
        output = generate_response(structured_prompt)
        print("\nAI Response:")
        print(output)

        parsed = parse_output(output)
        print("\nParsed Output:")
        print(parsed)

def main():
    print("Risk Analysis Assistant Ready (DevQuasar Model + FAISS)")
    test_df = pd.read_csv("../data/test_scenario.csv")
    results = []
    for _, row in test_df.iterrows():
        scenario_text = row["User"]
        context = retrieve_context(scenario_text)
        structured_prompt = f"""
        You are an assistant in security risk analysis.
        Analyze the following risk scenario:

        Scenario:
        '{scenario_text}'

        Relevant Information:
        {context}

        Follow this structure:
        1. Identify threats (e.g., M1 - Queuing Access)
        2. Link vulnerabilities (e.g., V7 - Untested software)
        3. Classify risk type (Real/Potential)
        4. Propose mitigations (e.g., ISO 27001 controls)
        Respond **ONLY** in JSON format.
        """
        
        output = generate_response(structured_prompt)
        parsed_data = parse_output(output)
        results.append({
            "Scenario ID": row["Scenario ID"],
            "User Input": scenario_text,
            "AI Response": parsed_data
        })
    
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    InteractiveResult()
