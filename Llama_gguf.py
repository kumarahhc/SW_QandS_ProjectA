from llama_cpp import Llama

# Load the GGUF model
model_path = "llama-O1-Supervised-1129-q4_k_m.gguf"
llm = Llama(model_path=model_path)

# Function to generate text
def call_gpt(prompt):
    response = llm(prompt, max_tokens=50)
    return response["choices"][0]["text"]

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        response = call_gpt(user_input)
        print("AI:", response)
