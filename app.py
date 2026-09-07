import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set in .env")

genai.configure(api_key=api_key)

# System prompt defining bot role and identity
SYSTEM_INSTRUCTION = (
    "You are 'TechGuide', an AI assistant specializing in helping software "
    "engineering interns learn machine learning concepts. Be concise, encouraging, "
    "and provide short code snippets when helpful."
)

MAX_TURNS = 6  # Context management strategy: Maintain last 6 messages (3 user + 3 bot turns)

def run_chatbot():
    # Initialize Gemini model with system instruction
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )
    
    # In-memory storage for multi-turn history
    conversation_history = []

    print("--- TechGuide AI Chatbot Initialized (Type 'exit' or 'quit' to end) ---")

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation. Goodbye!")
                break

            # Append user message to history
            conversation_history.append({"role": "user", "parts": [user_input]})

            # Context Window Management Strategy: Truncate history to last N messages
            truncated_history = conversation_history[-MAX_TURNS:]

            # Send truncated history to Gemini API
            response = model.generate_content(truncated_history)

            # Extract response text
            bot_reply = response.text
            print(f"\nTechGuide: {bot_reply}")

            # Append bot reply to history
            conversation_history.append({"role": "model", "parts": [bot_reply]})

        except Exception as e:
            print(f"\n[Error]: Unable to process your request. {str(e)}")
            print("Please check your network connection or API quota and try again.")

if __name__ == "__main__":
    run_chatbot()
