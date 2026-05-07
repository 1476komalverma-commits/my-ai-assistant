import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_ai(user_message):
    """
    Send a message to the AI and get a response
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """
    Main function to run the chatbot
    """
    print("=" * 50)
    print("Welcome to My AI Assistant Demo!")
    print("=" * 50)
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if not user_input:
            print("Please enter a message.\n")
            continue
        
        print("\nAssistant: ", end="")
        response = chat_with_ai(user_input)
        print(response)
        print()

if __name__ == "__main__":
    main()
