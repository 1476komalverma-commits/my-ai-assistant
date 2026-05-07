import os
from dotenv import load_dotenv
import openai
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'database': os.getenv("DB_NAME", "ai_assistant"),
    'user': os.getenv("DB_USER", "postgres"),
    'password': os.getenv("DB_PASSWORD"),
    'port': os.getenv("DB_PORT", "5432")
}

def get_db_connection():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

def init_database():
    """Initialize database and create table if it doesn't exist"""
    conn = get_db_connection()
    if not conn:
        print("Could not connect to database!")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

def save_message(user_msg, assistant_msg):
    """Save user message and AI response to PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (user_message, assistant_response)
            VALUES (%s, %s)
        ''', (user_msg, assistant_msg))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving message: {str(e)}")
        return False

def get_chat_history():
    """Retrieve chat history from PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            SELECT * FROM chat_messages 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        return messages
    except Exception as e:
        print(f"Error retrieving history: {str(e)}")
        return []

def chat_with_ai(user_message):
    """Send a message to the AI and get a response"""
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

def display_chat_history():
    """Display chat history from database"""
    history = get_chat_history()
    if not history:
        print("\nNo chat history found.\n")
        return
    
    print("\n" + "=" * 50)
    print("CHAT HISTORY (Last 10 messages)")
    print("=" * 50)
    
    for msg in reversed(history):
        print(f"\n[{msg['timestamp']}]")
        print(f"You: {msg['user_message']}")
        print(f"Assistant: {msg['assistant_response']}")
    
    print("\n" + "=" * 50 + "\n")

def main():
    """Main function to run the chatbot"""
    # Initialize database
    if not init_database():
        print("Failed to initialize database. Exiting...")
        return
    
    print("=" * 50)
    print("Welcome to My AI Assistant Demo!")
    print("=" * 50)
    print("Type 'quit' to exit")
    print("Type 'history' to see chat history\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if user_input.lower() == 'history':
            display_chat_history()
            continue
        
        if not user_input:
            print("Please enter a message.\n")
            continue
        
        print("\nAssistant: ", end="")
        response = chat_with_ai(user_input)
        print(response)
        
        # Save to database
        if save_message(user_input, response):
            print("(✅ Message saved to database)")
        else:
            print("(⚠️ Could not save message)")
        
        print()

if __name__ == "__main__":
    main()
