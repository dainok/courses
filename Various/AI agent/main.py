from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create an instance of the OpenAI class
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_text_with_conversation(messages, model = "gpt-3.5-turbo"):
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages
        )
    return response.choices[0].message.content

# Define a list of messages to simulate a conversation
test_messages = [
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "system", "content": "You are a helpful AI assistant"}
]

# Call the function with the test messages
response = generate_text_with_conversation(test_messages)
print("AI Response:", response)
