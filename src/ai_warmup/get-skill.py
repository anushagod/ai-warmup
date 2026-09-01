import os
import sys

from dotenv import load_dotenv
from litellm import completion

load_dotenv()

# 1. Load Environment Variables
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("❌ Error: Missing OpenAI API key in .env file.")
    sys.exit(1)

# 2. Define Skills and Prompts
SKILLS_PROMPTS = {
    "code_reviewer": "You are an expert software architect. Review this code for bugs, efficiency, and security vulnerabilities.",
    "copywriter": "You are a creative advertising copywriter. Rewrite this text to be highly engaging, punchy, and persuasive.",
    "summarizer": "You are a precise data analyst. Condense this information into brief, high-impact bullet points focusing on metrics.",
}

# 3. Define a default skill if the user doesn't provide one
DEFAULT_SKILL = "summarizer"  

# 4. Function to get skill from command line arguments
def get_skill_prompt():
    """Parses command-line arguments to select a skill prompt."""
    if len(sys.argv) > 1:
        chosen_skill = sys.argv[1].lower()
        print(f"🎛️ Requested skill: '{chosen_skill}'")
    else:
        chosen_skill = DEFAULT_SKILL
        print(f"ℹ️ No skill argument provided. Falling back to default: '{chosen_skill}'")

    if chosen_skill in SKILLS_PROMPTS:
        return SKILLS_PROMPTS[chosen_skill]
    else:
        print(f"⚠️ Skill '{chosen_skill}' not found. Using default instructions.")
        return SKILLS_PROMPTS[DEFAULT_SKILL]
    
# 5. Function to call the LLM API using litellm
def get_skill(system_instruction: str, text: str):
    # Formulate structural messages using the correct chat role format
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": text}
    ]
    
    try:
        print("🤖 Contacting LLM...")
        # Call the completion function from litellm
        response = completion(
            model="openai/gpt-4o-mini", # Explicitly declaring 'openai/' prefix handles any fallbacks gracefully
            messages=messages,
            max_tokens=150,
            temperature=0.7,
            api_key=openai_key
        )
        return response
    except Exception as e:
        print(f"❌ API Call failed: {e}")
        sys.exit(1)

# Execution Flow
system_instruction = get_skill_prompt()
text_to_process = "This is a sample text that needs to be summarized. It contains multiple sentences and details that should be condensed into a brief summary."

# Get response and extract text cleanly
response = get_skill(system_instruction, text_to_process)
output_text = response.choices[0].message.content

print("\n✨ LLM Response:")
print(output_text)
