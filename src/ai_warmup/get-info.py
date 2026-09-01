import os;
import sys;

from dotenv import load_dotenv;
from litellm import completion;

load_dotenv();

# 1. Load Environment Variables
openai_key = os.getenv("OPENAI_API_KEY");

if not openai_key:
    print("❌ Error: Missing OpenAI API key in .env file.");
    sys.exit(1);

def get_info(model_name: str, prompt: str):
    print(f"🚀 Calling {model_name}...");
    resp = completion(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides information about the model you are using and outputs JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    );

    print(f"📩 Response: {resp.choices[0].message.content}")
    print(f"📩 Tokens Used: {resp.usage.total_tokens}");

get_info_prompt = """
                    extract order number, email and customer name from the given paragraph: 
                    'Hello, I recently placed an order with your company. My order number is 12345. 
                     My email is john.doe@example.com and my customer name is John Doe.'""";

# Test OpenAI
get_info("openai/gpt-4o-mini", get_info_prompt);