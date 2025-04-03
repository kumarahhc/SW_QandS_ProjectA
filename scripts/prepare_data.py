import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

def prepare_data():
    vul_df=pd.read_csv("../data/Vulnerability.csv")
    threat_df=pd.read_csv("../data/Threats.csv")
    #risk_analysis_df=pd.read_csv("../data/RiskAnalysis.csv")
    
    chunks=[]
    metadata=[]
    
    for _, row in vul_df.iterrows():
        text=f"Vulnerability {row['ID']} ({row['VULNERABILITY']}): {row['DESCRIPTION']}"
        chunks.append(text)
        metadata.append({
            "type":"vulnarability",
            "id":row["ID"],
            "title":row["VULNERABILITY"],
            "description":row["DESCRIPTION"]
        })
    for _, row in threat_df.iterrows():
        text=f"Threat {row['THREAT ID']} ({row['THREAT']}): {row['DESCRIPTION']}"
        chunks.append(text)
        metadata.append({
            "type":"threat",
            "id":row["THREAT ID"],
            "title":row["THREAT"],
            "description":row["DESCRIPTION"]
        })
    """   
    for _, row in risk_analysis_df.iterrows():
        text=f"Risk Analysis {row['THREAT ID']} ({row['THREAT']}) :({row['VULNERABILITY ID']}) ({row['VULNERABILITY']}) : ({row['COUNTERMEASURE ID']}) {row['COUNTERMEASURE']}"
        chunks.append(text)
        metadata.append({
            "type":"counter measure",
            "id":row["COUNTERMEASURE ID"],
            "title":row["COUNTERMEASURE"],
            "description":row["COUNTERMEASURE"]
        })
    """
    return chunks,metadata

def build_vector_db():
    text,metadata=prepare_data()
    model=SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeddings=model.encode(text)
    
    dim=embeddings.shape[1]
    index=faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    
    faiss.write_index(index,"vector_db.index")
    with open("metadata.pkl","wb") as f:
        pickle.dump(metadata,f)
        
    print(f"DB Indexed created")
    
    
if __name__ == "__main__":
    build_vector_db()