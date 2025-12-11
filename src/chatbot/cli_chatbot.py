import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.retrieval.retriever import Retriever


CONFIDENCE_THRESHOLD = 0.2  

def main():
    print("=== Morocco Tourism Chatbot ===")
    print("Type your questions about Morocco, or 'quit' to exit.\n")

    retriever = Retriever()

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit']:
            print("Chatbot: Goodbye! Enjoy your trip to Morocco!")
            break

   


        
        responses = retriever.get_answer(user_input)

        
        best_answer, confidence_score = responses[0]

        
        if confidence_score < CONFIDENCE_THRESHOLD:
            print("Chatbot: I apologize, that seems to be outside my knowledge base. I can only answer questions about Morocco tourism.\n")
        else:
            print(f"Chatbot: {best_answer}\n")

if __name__ == "__main__":
    main()
