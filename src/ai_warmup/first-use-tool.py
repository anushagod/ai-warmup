import os
import sys
import json

from dotenv import load_dotenv
from litellm import completion

load_dotenv()   
# 1. Load Environment Variables
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("❌ Error: Missing OpenAI API key in .env file.")
    sys.exit(1)

def get_weather(location: str):
    database = {"New York": "Sunny, 72°F", "Los Angeles": "Cloudy, 68°F", "Chicago": "Rainy, 60°F"}
    return database.get(location, f"Weather for {location} is unknown.")

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Provides the current weather for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location for which to retrieve the current weather."
                    }
                },
                "required": ["location"]
            }
        }
    }
]

def use_tool(model_name: str, prompt: str):
    messages = [
        {"role": "system", "content": "Assist the user with information based on the current weather."},
        {"role": "user", "content": prompt}
    ]
    
    # Map string names directly to your python functions
    tool_functions = {"get_weather": get_weather}

    while True:
        # A single completion call handles all steps in the cycle
        # We pass tools_schema every turn because the LLM is stateless
        response = completion(
            model=model_name,
            messages=messages,
            tools=tools_schema,
        )

        assistant_message = response.choices[0].message
        messages.append(assistant_message)

        # Check if the model wants to call tools
        if tool_calls := assistant_message.tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                if func_name in tool_functions:
                    args = json.loads(tool_call.function.arguments)
                    location = args.get("location")
                    
                    # Execute the matched tool function dynamically
                    weather_info = tool_functions[func_name](location)
                    print(f"Tool Call: {func_name}({location}) => {weather_info}")
                    
                    # Append execution context back to history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": weather_info
                    })
            # Continue the loop to let the stateless LLM look at the tool results
            continue 
            
        else:
            # If no tool calls were requested, this is your final answer
            print("\nFinal Response:")
            print(assistant_message.content)
            break
    
text_prompt = "Should I carry an umbrella today in New York?"
# Test OpenAI
use_tool("openai/gpt-4o-mini", text_prompt)
