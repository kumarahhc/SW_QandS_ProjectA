from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# Load standards into a vector database
def setup_rag():
    # Example standards (replace with PCM-ANS TI-002 or other relevant standards)
    standards = [
        "PCM-ANS TI-002: Secure authentication mechanisms must be implemented.",
        "PCM-ANS TI-002: Untested software applications are considered vulnerabilities.",
        "PCM-ANS TI-002: Asynchronous attacks must be mitigated through proper access controls."
    ]
    
    # Use HuggingFace embeddings ( model installed)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create FAISS vector store
    db = FAISS.from_texts(standards, embeddings)
    return db

# Function to retrieve context and generate RAG-augmented prompt
def get_rag_prompt(prompt, db, k=3):
    """Retrieve relevant context and augment the prompt."""
    docs = db.similarity_search(prompt, k=k)
    context = "\n".join([doc.page_content for doc in docs])
    rag_prompt = f"Context: {context}\n\nQuestion: {prompt}\nAnswer:"
    return rag_prompt

if __name__ == "__main__":
    # Set up RAG
    db = setup_rag()
    
    # Test RAG-augmented prompt generation
    user_input = "A system uses untested SSO functionality."
    rag_prompt = get_rag_prompt(user_input, db)
    print("RAG-Augmented Prompt:")
    print(rag_prompt)