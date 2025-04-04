import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from llama_cpp import Llama
import re
import pandas as pd

"""RAG asisted model to run the test"""
#Initialize the model
model_path = "OpenO1-LLama-8B-v0.1.Q6_K.gguf"
##model_path = "llama-O1-Supervised-1129-q4_k_m.gguf"
llm = Llama(model_path=model_path,n_ctx=2048,n_threads=4,n_batch=512,verbose=False)  # Load the model

# Load Vector DB and metadata
index = faiss.read_index("vector_db.index")
with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# Embedding Model (same one used in indexing)
embed_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def retrieve_context(query, top_k=1):
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

def analyze_security_risk(user_input,rag):
    # Define the prompt with explicit instructions for JSON format
    if(rag):
        context = retrieve_context(user_input)
        context= f"Relevant Context:{context}"
    else:
        context=""
        
    prompt = f"""SYSTEM: You are a security analyst. You MUST output ONLY the JSON array, nothing else.
    Follow EXACTLY this format:
    {{
    "Extended": "...",
    "Short": "YES/NO/MORE",
    "Details": "...",
    "RiskID": "...",
    "RiskDesc": "...",
    "VulnID": "...",
    "VulnDesc": "...",
    "RiskType": "Real/Potential"
    }}
    User Input: '{user_input}'
    {context}
    """
    
    output = llm(prompt, max_tokens=512, temperature=0, top_p=0.9, repeat_penalty=1.5,echo=False)  # Generate response
    
    # Print the raw output from the model for debugging
    print("Model raw output:", output["choices"][0]["text"])

    # Clean the output by removing any non-JSON text
    raw_output = output["choices"][0]["text"].strip()
    return raw_output

def runTest(rag):
    if(rag):
        print("RAG Assistant (LLaMA + FAISS Vector DB) is used to geratare result")
    
    test_df=pd.read_csv("../data/test_scenario.csv")
    results = []
    for _, row in test_df.iterrows():
        scenario_text=row["User"]
               
        if(rag):
            # Retrieve Relevant Context 
            context = retrieve_context(scenario_text)
            context= f"Relevant Context:{context}"
        else:
            context=""
        
        prompt = f"""
        You are an assistant specialized in security risk analysis.
        Your task is to determine if the given user message contains a security threat.

        IMPORTANT: Do not retunr the input message in reply.
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
        '{scenario_text}'
        {context}
        """
        
        output = analyze_security_risk(prompt,rag)
        # Parse Output to JSON
        parsed_data = parse_output(output)
        # Append Results
        results.append({
            "Scenario ID": row["Scenario ID"],
            "User Input": scenario_text,
            "JSON": parsed_data,
            "AI Result":output
        })
            
    # Save Results to JSON File
    with open("../data/test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

def InteractiveResult(rag):
    while True:
        user_input = input("\nEnter a risk scenario (User Messagee): ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        analysis_result = analyze_security_risk(user_input,rag)
        if(rag):
            # Parse Output to JSON
            parsed_data = parse_output(analysis_result)
            print(json.dumps(parsed_data, indent=4))
        else:
            # Append Results
            print(analysis_result)
        

def parse_output(response):
    """Parse the model's output into structured data."""
    json_cleaned_output = re.search(r"\[\s*\{.*?\}\s*\]", response, re.DOTALL)
    
    if json_cleaned_output:
        # Clean the output to ensure it's a valid JSON array
        raw_json = json_cleaned_output.group().strip()
        
        # Remove unwanted text like '[Output], [END OF OUTPUT]' from the start and any other non-JSON elements
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
# Example usage
if __name__ == "__main__":
    """Run Interactive Model (Pass True to use RAG) For testing"""
    #InteractiveResult(False)
    """Run Test at once using testing data set"""
    runTest(True) # True to use the RAG setup
