import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import json
import re
from typing import Union
from llama_cpp import Llama

class SecurityRAGSystem:
    def __init__(self):
        # Initialize embedding model
        self.embed_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        # Load vector database
        try:
            self.index = faiss.read_index("vector_db.index")
            with open("metadata.pkl", "rb") as f:
                self.metadata = pickle.load(f)
            print("RAG system initialized with vector DB")
        except Exception as e:
            print(f"Error loading RAG index: {e}")
            self.index = None

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant security context"""
        if not self.index:
            return ""
            
        query_embed = self.embed_model.encode([query])
        distances, indices = self.index.search(query_embed.astype('float32'), top_k)
        
        context = "\n=== Relevant Security Context ==="
        for i in indices[0]:
            item = self.metadata[i]
            context += f"\n[{item['type'].upper()}] {item['title']} (ID: {item['id']}): {item['description']}"
        
        return context

# Initialize systems
rag = SecurityRAGSystem()
llm = Llama(
    model_path="llama-2-7b-chat.Q6_K.gguf",
    chat_format="llama-2",
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=0
)

def analyze_security(scenario: str, use_rag: bool = True) -> dict:
    """Generate analysis with RAG context"""
    context = rag.retrieve_context(scenario) if (use_rag and rag.index) else ""
    
    messages = [
        {
            "role": "system",
            "content": """As a security analyst, return ONLY this JSON structure:
            {
                "Extended": "detailed risk impact",
                "Short": "YES/NO/MORE",
                "Details": "specific vulnerabilities",
                "RiskID": "e.g., SEC-001",
                "RiskDesc": "risk category",
                "VulnID": "e.g., CWE-287",
                "VulnDesc": "vulnerability type", 
                "RiskType": "Real/Potential"
            }"""
        },
        {
            "role": "user",
            "content": f"Scenario: {scenario}{context}"
        }
    ]
    
    response = llm.create_chat_completion(
        messages=messages,
        temperature=0.1,
        max_tokens=512,
        stop=["}\n"]
    )
    
    return parse_output(response['choices'][0]['message']['content'])

def parse_output(raw: str) -> dict:
    """Robust JSON extraction"""
    try:
        # Handle both string and pre-parsed JSON
        if isinstance(raw, dict):
            return raw
            
        json_str = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_str:
            raise ValueError("No JSON found")
            
        result = json.loads(json_str.group())
        
        # Validate required fields
        required = ["Extended", "Short", "Details", "RiskID", 
                  "RiskDesc", "VulnID", "VulnDesc", "RiskType"]
        for field in required:
            if field not in result:
                raise ValueError(f"Missing field: {field}")
                
        return result
        
    except Exception as e:
        print(f"! Output parsing failed: {e}")
        return {"error": "Invalid analysis output"}

def interactive_session(use_rag: bool = True):
    print(f"\n🔒 Security Analyzer {'(RAG Enabled)' if use_rag else ''}")
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
            result = analyze_security(scenario, use_rag)
            print(json.dumps(result, indent=2))
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nSession ended.")
            break

if __name__ == "__main__":
    # Initialize RAG system (will load existing vector DB)
    rag = SecurityRAGSystem()
    
    # Start interactive session with RAG
    interactive_session(use_rag=True)