import pandas as pd

# Load vulnerabilities and Threats datasets
def setup_rag():
    vulnarabilities=pd.read_csv("../data/Vulnarability.csv")
    threats=pd.read_csv("../data/Threats.csv")
    return vulnarabilities,threats

def get_rag_prompt(user_message,vulnarabilities, threats):
    

if __name__ == "__main__":
    # Set up RAG
    db = setup_rag()
    #db = FAISS.load_local("faiss_index", embeddings)  ---------------------------->
    # Test RAG-augmented prompt generation
    user_input = "A system uses untested SSO functionality."
    rag_prompt = get_rag_prompt(user_input, db)
    print("RAG-Augmented Prompt:")
    print(rag_prompt)