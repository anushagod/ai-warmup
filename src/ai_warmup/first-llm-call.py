import os
import sys

from dotenv import load_dotenv
from litellm import completion

load_dotenv()

# 1. Load Environment Variables
openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

if not openai_key or not anthropic_key:
    print("❌ Error: Missing API keys in .env file.")
    sys.exit(1)

def test_model(model_name: str, prompt: str):
    print(f"🚀 Calling {model_name}...")
    resp = completion(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    print(f"📩 Response: {resp.choices[0].message.content.strip()}")
    print(f"📊 Tokens Used: {resp.usage.total_tokens}\n")

test_prompt = "Explain in 1 sentence why microservices use asynchronous queues."

# Test OpenAI
test_model("openai/gpt-4o-mini", test_prompt)

# Test Anthropic
test_model("anthropic/claude-haiku-4-5-20251001", test_prompt)